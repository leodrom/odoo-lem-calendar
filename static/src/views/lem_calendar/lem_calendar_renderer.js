import { CalendarRenderer } from "@web/views/calendar/calendar_renderer";
import { LemCalendarCommonRenderer } from "./lem_calendar_common_renderer";

export class LemCalendarRenderer extends CalendarRenderer {
    static components = {
        ...CalendarRenderer.components,
        day: LemCalendarCommonRenderer,
        week: LemCalendarCommonRenderer,
        month: LemCalendarCommonRenderer,
    };
}
