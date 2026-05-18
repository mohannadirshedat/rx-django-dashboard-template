import reflex as rx

from analytics.models import DailyMetric, DevicePeriod, DeviceShare, KpiKey, KpiSnapshot, MetricType
from reflex_django.auth.decorators import login_required
from reflex_django.state import AppState

_CHART_KEYS = {
    MetricType.USERS: ("Users", "users_data"),
    MetricType.REVENUE: ("Revenue", "revenue_data"),
    MetricType.ORDERS: ("Orders", "orders_data"),
}

_KPI_ATTRS = {
    KpiKey.USERS: ("kpi_users", "kpi_users_prev"),
    KpiKey.REVENUE: ("kpi_revenue", "kpi_revenue_prev"),
    KpiKey.ORDERS: ("kpi_orders", "kpi_orders_prev"),
}


class OverviewState(AppState):
    area_toggle: bool = True
    selected_tab: str = "users"
    timeframe: str = "Monthly"
    users_data: list[dict] = []
    revenue_data: list[dict] = []
    orders_data: list[dict] = []
    device_data: list[dict] = []
    yearly_device_data: list[dict] = []
    kpi_users: int = 0
    kpi_users_prev: int = 0
    kpi_revenue: int = 0
    kpi_revenue_prev: int = 0
    kpi_orders: int = 0
    kpi_orders_prev: int = 0
    welcome_name: str = ""

    @rx.event
    def set_timeframe(self, value: str):
        self.timeframe = value

    @rx.event
    def set_selected_tab(self, tab: str | list[str]):
        self.selected_tab = tab if isinstance(tab, str) else tab[0]

    @rx.event
    def toggle_areachart(self):
        self.area_toggle = not self.area_toggle

    @rx.event
    @login_required
    async def load_metrics(self):
        await self.refresh_django_user_fields()
        from accounts.utils import aget_or_create_profile

        user = self.request.user #current_user()
        if user.is_authenticated:
            profile = await aget_or_create_profile(user)
            self.welcome_name = profile.display_name or user.get_username()
        else:
            self.welcome_name = "Guest"

        async for snapshot in KpiSnapshot.objects.all():
            attrs = _KPI_ATTRS.get(snapshot.key)
            if attrs:
                value_attr, prev_attr = attrs
                setattr(self, value_attr, snapshot.value)
                setattr(self, prev_attr, snapshot.previous_value)

        users_data: list[dict] = []
        revenue_data: list[dict] = []
        orders_data: list[dict] = []

        async for metric in DailyMetric.objects.all().order_by("date"):
            label, _ = _CHART_KEYS[metric.metric_type]
            date_label = metric.date.strftime("%m-%d")
            point = {"Date": date_label, label: metric.value}
            if metric.metric_type == MetricType.USERS:
                users_data.append(point)
            elif metric.metric_type == MetricType.REVENUE:
                revenue_data.append(point)
            else:
                orders_data.append(point)

        self.users_data = users_data
        self.revenue_data = revenue_data
        self.orders_data = orders_data

        device_data: list[dict] = []
        async for device in DeviceShare.objects.filter(period=DevicePeriod.MONTHLY):
            device_data.append(
                {"name": device.name, "value": device.value, "fill": device.fill}
            )
        self.device_data = device_data

        yearly_device_data: list[dict] = []
        async for device in DeviceShare.objects.filter(period=DevicePeriod.YEARLY):
            yearly_device_data.append(
                {"name": device.name, "value": device.value, "fill": device.fill}
            )
        self.yearly_device_data = yearly_device_data
