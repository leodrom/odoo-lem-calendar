/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

const COLORS = [
    "#E53935", "#D81B60", "#8E24AA", "#5E35B1",
    "#3949AB", "#1E88E5", "#039BE5", "#00ACC1",
    "#00897B", "#43A047", "#7CB342", "#C0CA33",
    "#FDD835", "#FFB300", "#FB8C00", "#F4511E",
    "#6D4C41", "#757575", "#546E7A", "#37474F",
    "#FF7043", "#26A69A", "#42A5F5", "#AB47BC",
];

export class ColorPicker24 extends Component {
    static template = "lem_calendar.ColorPicker24";
    static props = { ...standardFieldProps };

    get colors() {
        return COLORS;
    }

    selectColor(color) {
        this.props.record.update({ [this.props.name]: color });
    }
}

registry.category("fields").add("color_picker_24", {
    component: ColorPicker24,
    supportedTypes: ["char"],
});
