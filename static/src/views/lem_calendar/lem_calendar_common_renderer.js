import { CalendarCommonRenderer } from "@web/views/calendar/calendar_common/calendar_common_renderer";

const STATUS_BORDER_COLOR = {
    negotiation: "#f0ad4e",
    confirmed:   "#28a745",
    reserve:     "#17a2b8",
    waiting:     "#fd7e14",
    cancelled:   "#dc3545",
};

export class LemCalendarCommonRenderer extends CalendarCommonRenderer {
    eventClassNames(info) {
        const classNames = super.eventClassNames(info);
        const record = this.props.model.records[info.event.id];
        const status = record?.rawRecord?.status;
        if (status) {
            classNames.push(`o_lem_event_status_${status}`);
        }
        return classNames;
    }

    onEventDidMount(info) {
        super.onEventDidMount(info);
        const record = this.props.model.records[info.event.id];
        const status = record?.rawRecord?.status;
        if (status && STATUS_BORDER_COLOR[status]) {
            info.el.style.borderLeft = `4px solid ${STATUS_BORDER_COLOR[status]}`;
            info.el.style.borderRadius = "3px";
        }
    }
}
