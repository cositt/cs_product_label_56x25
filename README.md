# cs_product_label_56x25

Etiqueta de producto **56 x 25 mm en PDF** para Odoo 19, pensada para la Zebra ZD220d
de Pequeño Planeta (USB, sin IoT, driver Windows «ZDesigner ZD220-203dpi ZPL»).

## Qué hace

- Añade el formato **«Tienda 56 x 25 mm»** al asistente *Imprimir etiquetas*
  (Productos, variantes y recepciones). Es el formato por defecto; los demás siguen igual.
- Una etiqueta por página de 56 x 25 mm: nombre (2 líneas), variante (talla/color),
  referencia, precio y código de barras (EAN-13 si es válido, si no Code128;
  sin código de barras → etiqueta sin barras).
- **Precio**: de la tarifa del asistente. Por defecto, la del parámetro de sistema
  `cs_product_label_56x25.pricelist_id` y, si no existe, la que Odoo aplica al usuario
  (en Pequeño Planeta = tarifa 2 «Woo bebemalaga Pricelist»). Igual que Odoo, no añade impuestos.
- **Impresión directa**: en vez de descargar el PDF, abre el diálogo de impresión del
  navegador. Si algo falla, vuelve al comportamiento normal (descarga).
- Añade el formato a *Tipo de operación → Imprimir etiquetas automáticamente* (recepciones).
- Decodifica nombres con entidades HTML importados de Woo (`Molis&amp;Co` → `Molis&Co`).
  No modifica datos.

## Despliegue (SRV)

1. Copia de seguridad de `db-pequeno-planeta`.
2. Copiar la carpeta a `/opt/saas/clientes/pequeno-planeta/addons-extra/`.
3. `docker restart odoo-pequeno-planeta` y después `nginx -t && nginx -s reload`.
4. Aplicaciones → Actualizar lista → instalar «Etiqueta de producto 56 x 25 mm».
5. (Opcional) Ajustes → Técnico → Parámetros del sistema:
   `cs_product_label_56x25.pricelist_id` = `2`.

## En la tienda (una vez)

1. Rollo 56 x 25 cargado y calibrado (botón FEED mantenido hasta 2 parpadeos).
2. Windows → Impresoras → la ZDesigner que esté **en línea** (hay dos, una «(Copiar 1)»
   sin conexión) → Preferencias: papel 56 x 25 mm, térmico directo.
3. Primera impresión desde Chrome: impresora ZDesigner, márgenes **Ninguno**,
   escala **100 %** / «Tamaño real». Chrome lo recuerda.
4. Sin diálogo (opcional): acceso directo de Chrome con `--kiosk-printing` y la Zebra como
   impresora predeterminada de Windows. Afecta a todo lo que se imprima desde ese Chrome
   y solo funciona si Chrome no estaba ya abierto.

## Tests

`odoo -d <db> -i cs_product_label_56x25 --test-enable --test-tags=/cs_product_label_56x25`
(10 tests: formato, papel, otros formatos intactos, tarifa por defecto, variantes/precio/
barcode, cantidades de recepción). El JS no tiene test automático.
