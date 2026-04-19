/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
        this.openfactura_document_type = this.openfactura_document_type || this.pos.config.openfactura_default_document_type || "receipt";
    },
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.openfactura_document_type = this.openfactura_document_type;
        return json;
    },
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.openfactura_document_type = json.openfactura_document_type || "receipt";
    },
});

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        const order = this.currentOrder;
        if (order.openfactura_document_type === "invoice" && !order.get_partner()) {
            this.notification.add("Para emitir factura debe seleccionar cliente.", { type: "danger" });
            return;
        }
        return super.validateOrder(isForceValidate);
    },
    setOpenfacturaDocType(type) {
        this.currentOrder.openfactura_document_type = type;
        this.render();
    },
});
