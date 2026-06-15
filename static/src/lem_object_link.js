import { registry } from "@web/core/registry";

registry.category("services").add("lem_object_link", {
    dependencies: ["action"],
    start(env, { action }) {
        document.addEventListener("click", (ev) => {
            const a = ev.target.closest(".o_lem_object_link");
            if (!a) return;
            ev.preventDefault();
            ev.stopPropagation();
            const resModel = a.dataset.model;
            const resId = parseInt(a.dataset.id, 10);
            if (resModel && resId) {
                action.doAction({
                    type: "ir.actions.act_window",
                    res_model: resModel,
                    res_id: resId,
                    views: [[false, "form"]],
                    target: "current",
                });
            }
        }, { capture: true });
    },
});
