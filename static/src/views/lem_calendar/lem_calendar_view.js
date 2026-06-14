import { registry } from "@web/core/registry";
import { calendarView } from "@web/views/calendar/calendar_view";
import { LemCalendarRenderer } from "./lem_calendar_renderer";
import { LemCalendarModel } from "./lem_calendar_model";

export const lemCalendarView = {
    ...calendarView,
    type: "lem_calendar",
    Renderer: LemCalendarRenderer,
    Model: LemCalendarModel,
};

registry.category("views").add("lem_calendar", lemCalendarView);
