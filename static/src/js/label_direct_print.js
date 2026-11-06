import { registry } from "@web/core/registry";
import { user } from "@web/core/user";
import { getReportUrl } from "@web/webclient/actions/reports/utils";

/**
 * Direct printing of the 56 x 25 mm product label, without IoT.
 *
 * Instead of downloading the PDF, it is loaded in a hidden iframe and the
 * browser print dialog is opened on it. With Chrome started with
 * `--kiosk-printing` and the label printer as default printer, the label is
 * printed with no dialog at all.
 *
 * Only this module's report is intercepted. On any problem the handler returns
 * false, so Odoo falls back to its standard behaviour (PDF download / error).
 */
export const LABEL_REPORT = "cs_product_label_56x25.report_label_56x25";
const FRAME_ID = "cs_label_56x25_print_frame";
const PRINT_DELAY_MS = 500; // Chrome's PDF viewer needs a moment after load

let lastBlobUrl = null;

function printInHiddenFrame(blobUrl) {
    return new Promise((resolve, reject) => {
        document.getElementById(FRAME_ID)?.remove();
        const frame = document.createElement("iframe");
        frame.id = FRAME_ID;
        frame.style.cssText = "position:fixed;right:0;bottom:0;width:0;height:0;border:0;";
        frame.onload = () => {
            setTimeout(() => {
                try {
                    frame.contentWindow.focus();
                    frame.contentWindow.print();
                    resolve();
                } catch (error) {
                    reject(error);
                }
            }, PRINT_DELAY_MS);
        };
        frame.onerror = reject;
        frame.src = blobUrl;
        document.body.appendChild(frame);
    });
}

async function fetchLabelPdf(action) {
    const context = { ...user.context, ...(action.context || {}) };
    const url = getReportUrl({ ...action, context }, "pdf");
    const response = await fetch(url, { credentials: "same-origin" });
    const contentType = response.headers.get("content-type") || "";
    if (!response.ok || !contentType.includes("application/pdf")) {
        throw new Error(`Unexpected label response: ${response.status} ${contentType}`);
    }
    return response.blob();
}

export async function labelDirectPrintHandler(action, options, env) {
    if (action.report_name !== LABEL_REPORT || action.report_type !== "qweb-pdf") {
        return false;
    }
    env.services.ui.block();
    try {
        const blob = await fetchLabelPdf(action);
        if (lastBlobUrl) {
            URL.revokeObjectURL(lastBlobUrl);
        }
        lastBlobUrl = URL.createObjectURL(blob);
        await printInHiddenFrame(lastBlobUrl);
        return true;
    } catch (error) {
        console.warn("[cs_product_label_56x25] direct print failed, falling back to download", error);
        return false;
    } finally {
        env.services.ui.unblock();
    }
}

registry
    .category("ir.actions.report handlers")
    .add("cs_product_label_56x25_direct_print", labelDirectPrintHandler);
