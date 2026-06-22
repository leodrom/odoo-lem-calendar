import { CalendarCommonPopover } from "@web/views/calendar/calendar_common/calendar_common_popover";
import { useService } from "@web/core/utils/hooks";

const NOTES_LIMIT = 300;

export class LemCalendarPopover extends CalendarCommonPopover {
    static template = "lem_event_calendar.CalendarPopover";
    static subTemplates = {
        ...CalendarCommonPopover.subTemplates,
        body: "lem_event_calendar.CalendarPopover.body",
        footer: "lem_event_calendar.CalendarPopover.footer",
    };

    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
    }

    get notesInfo() {
        const raw = this.props.record.rawRecord.description;
        if (!raw) return null;
        const tmp = document.createElement("div");
        tmp.innerHTML = raw;
        const text = (tmp.textContent || tmp.innerText || "").trim();
        if (!text) return null;
        if (text.length <= NOTES_LIMIT) {
            return { html: raw, truncated: false };
        }
        const snippet = text.slice(0, NOTES_LIMIT)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
        return { html: snippet, truncated: true };
    }

    async onDuplicateEvent() {
        const record = this.props.record;
        try {
            await this.orm.call(
                this.props.model.resModel,
                "copy",
                [record.id],
                {}
            );
            this.props.close();
            await this.props.model.load();
            this.notification.add("Запис продубльовано", { type: "success" });
        } catch (e) {
            this.notification.add("Помилка при дублюванні", { type: "danger" });
        }
    }
}
