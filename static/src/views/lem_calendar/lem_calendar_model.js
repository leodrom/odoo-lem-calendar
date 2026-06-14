import { CalendarModel } from "@web/views/calendar/calendar_model";

const STATUS_COLOR = {
    negotiation: "#f0ad4e",
    confirmed:   "#28a745",
    reserve:     "#17a2b8",
    waiting:     "#fd7e14",
    cancelled:   "#dc3545",
};

export class LemCalendarModel extends CalendarModel {
    addFilterFields(record, filterInfo) {
        if (filterInfo.fieldName === "status") {
            const status = record.rawRecord.status;
            return { colorIndex: STATUS_COLOR[status] || "#aaaaaa" };
        }
        return super.addFilterFields(record, filterInfo);
    }
}
