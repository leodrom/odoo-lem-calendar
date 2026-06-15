import { CalendarFilterSection } from "@web/views/calendar/calendar_filter_section/calendar_filter_section";
import { patch } from "@web/core/utils/patch";

const ENTRY_TYPE_ORDER = { manual: 0, event: 1, lead: 2 };

patch(CalendarFilterSection.prototype, {
    getSortedFilters() {
        if (this.section.fieldName === "entry_type") {
            return this.section.filters.slice().sort((a, b) => {
                const ai = ENTRY_TYPE_ORDER[a.value] ?? 999;
                const bi = ENTRY_TYPE_ORDER[b.value] ?? 999;
                return ai - bi;
            });
        }
        return super.getSortedFilters();
    },
});
