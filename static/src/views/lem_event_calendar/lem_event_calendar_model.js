import { CalendarModel } from "@web/views/calendar/calendar_model";

const STATUS_COLOR = {
    negotiation: "#f0ad4e",
    confirmed:   "#28a745",
    reserve:     "#17a2b8",
    waiting:     "#fd7e14",
    cancelled:   "#dc3545",
};

const ENTRY_TYPE_OPTIONS = [
    { value: "manual", label: "Невизначений" },
    { value: "event",  label: "Подія" },
    { value: "lead",   label: "Нагода" },
];

export class LemCalendarModel extends CalendarModel {
    setup(params, services) {
        super.setup(params, services);
        if (this.meta.filtersInfo?.entry_type) {
            this.meta.filtersInfo.entry_type.label = "Об'єкт";
        }
    }

    addFilterFields(record, filterInfo) {
        if (filterInfo.fieldName === "status") {
            const status = record.rawRecord.status;
            return { colorIndex: STATUS_COLOR[status] || "#aaaaaa" };
        }
        if (filterInfo.fieldName === "entry_type") {
            const ENTRY_TYPE_COLOR = {
                event:  "#28a745",
                lead:   "#17a2b8",
                manual: "#aaaaaa",
            };
            return { colorIndex: ENTRY_TYPE_COLOR[record.rawRecord.entry_type] || "#aaaaaa" };
        }
        return super.addFilterFields(record, filterInfo);
    }

    async loadDynamicFilterSection(data, fieldName, filterInfo, previousSection) {
        const section = await super.loadDynamicFilterSection(data, fieldName, filterInfo, previousSection);

        if (fieldName !== "entry_type") {
            return section;
        }

        const previousFilters = previousSection ? previousSection.filters : [];

        // Normalize labels for existing items
        for (const filter of section.filters) {
            const opt = ENTRY_TYPE_OPTIONS.find((o) => o.value === filter.value);
            if (opt) filter.label = opt.label;
        }

        // Add missing options
        for (const { value, label } of ENTRY_TYPE_OPTIONS) {
            if (!section.filters.find((f) => f.value === value)) {
                const previousFilter = previousFilters.find((f) => f.type === "dynamic" && f.value === value);
                section.filters.push({
                    type: "dynamic",
                    recordId: null,
                    value,
                    label,
                    active: previousFilter ? previousFilter.active : true,
                    canRemove: false,
                    colorIndex: null,
                    hasAvatar: false,
                });
            }
        }

        const labelOrder = ENTRY_TYPE_OPTIONS.map((o) => o.label);
        section.filters.sort((a, b) => {
            const ai = labelOrder.indexOf(a.label);
            const bi = labelOrder.indexOf(b.label);
            return (ai === -1 ? 999 : ai) - (bi === -1 ? 999 : bi);
        });

        return section;
    }
}
