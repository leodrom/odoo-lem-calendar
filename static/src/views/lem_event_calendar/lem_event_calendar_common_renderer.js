import { CalendarCommonRenderer } from "@web/views/calendar/calendar_common/calendar_common_renderer";
import { LemCalendarPopover } from "./lem_event_calendar_popover";

const STATUS_COLOR = {
    negotiation: "#f0ad4e",
    confirmed:   "#28a745",
    reserve:     "#17a2b8",
    waiting:     "#fd7e14",
    cancelled:   "#dc3545",
};

export class LemCalendarCommonRenderer extends CalendarCommonRenderer {
    static components = {
        ...CalendarCommonRenderer.components,
        Popover: LemCalendarPopover,
    };

    eventClassNames(info) {
        const classNames = super.eventClassNames(info);
        const record = this.props.model.records[info.event.id];
        if (!record) return classNames;

        const status = record.rawRecord.status;
        if (status) {
            classNames.push(`o_lem_event_status_${status}`);
        }

        const role = record.rawRecord.entry_role;
        if (role && role !== 'main') {
            classNames.push('o_event_hatched');
            classNames.push(`o_lem_role_${role}`);
        }

        return classNames;
    }

    onEventDidMount(info) {
        super.onEventDidMount(info);
        const record = this.props.model.records[info.event.id];
        if (!record) return;

        const status = record.rawRecord.status;

        // o_event_dot events (single-day timed events in month view) use
        // rgba(color, var(--o-bg-opacity)) for background — default opacity is unset
        // (transparent), only set to 1 on :hover. Force it always visible.
        if (info.el.classList.contains("o_event_dot")) {
            info.el.style.setProperty("--o-bg-opacity", "1");
        }

        // When no location color class was applied (colorIndex = 0/falsy),
        // fall back to status-based background color.
        if (!record.colorIndex) {
            info.el.style.backgroundColor = STATUS_COLOR[status] || "#aaaaaa";
        }

        if (status && STATUS_COLOR[status]) {
            info.el.style.borderLeft = `4px solid ${STATUS_COLOR[status]}`;
            info.el.style.borderRadius = "3px";
        }
    }
}
