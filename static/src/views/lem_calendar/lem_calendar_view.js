import { registry } from "@web/core/registry";
import { calendarView } from "@web/views/calendar/calendar_view";
import { LemCalendarRenderer } from "./lem_calendar_renderer";

export const lemCalendarView = {
    ...calendarView,
    type: "lem_calendar",
    Renderer: LemCalendarRenderer,
};

registry.category("views").add("lem_calendar", lemCalendarView);
