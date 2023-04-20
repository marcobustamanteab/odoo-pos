from odoo import models, fields
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class AccountMoveInvoiceReference(models.TransientModel):
    """
    Wizard to add an invoice reference.
    """
    _name = 'account.move.invoice.reference'
    _description = 'Account Move Invoice Reference'

    reference_documents = [
        ('29', '(29) Factura de Inicio'),
        ('30', '(30) Factura'),
        ('32', '(32) Factura de Ventas y Servicios no Afectos o Exentos de IVA'),
        ('33', '(33) Factura Electrónica'),
        ('34', '(34) Factura no Afecta o Exenta Electrónica'),
        ('35', '(35) Boleta de Venta'),
        ('38', '(38) Boleta exenta'),
        ('39', '(39) Boleta Electrónica'),
        ('40', '(40) Liquidación Factura'),
        ('41', '(41) Boleta Exenta Electrónica'),
        ('43', '(43) Liquidación Factura Electrónica'),
        ('45', '(45) Factura de Compra'),
        ('46', '(46) Factura de Compra Electrónica'),
        ('50', '(50) Guía de Despacho'),
        ('52', '(52) Guía de Despacho Electrónica'),
        ('55', '(55) Nota de Débito'),
        ('56', '(56) Nota de Débito Electrónica'),
        ('60', '(60) Nota de Crédito'),
        ('61', '(61) Nota de Crédito Electrónica'),
        ('70', '(70) Boleta de Honorarios'),
        ('71', '(71) Boleta de Honorarios Electrónica'),
        ('103', '(103) Liquidación'),
        ('108', '(108) SRF Solicitud de Registro de Factura'),
        ('110', '(110) Factura de Exportación Electrónica'),
        ('111', '(111) Nota de Débito de Exportación Electrónica'),
        ('112', '(112) Nota de Crédito de Exportación Electrónica'),
        ('500', '(500) Ajuste aumento Tipo de Cambio (código 500)'),
        ('501', '(501) Ajuste disminución Tipo de Cambio (código 501)'),
        ('801', '(801) Orden de Compra'),
        ('802', '(802) Nota de pedido'),
        ('803', '(803) Contrato'),
        ('804', '(804) Resolución'),
        ('805', '(805) Proceso ChileCompra'),
        ('806', '(806) Ficha ChileCompra'),
        ('807', '(807) DUS'),
        ('808', '(808) B/L (Conocimiento de embarque)'),
        ('809', '(809) AWB Airway Bill'),
        ('810', '(810) MIC/DTA'),
        ('811', '(811) Carta de Porte'),
        ('812', '(812) Resolución del SNA donde califica Servicios de Exportación'),
        ('813', '(813) Pasaporte'),
        ('814', '(814) Certificado de Depósito Bolsa Prod. Chile.'),
        ('815', '(815) Vale de Prenda Bolsa Prod. Chile'),
        ('901', '(901) Factura de ventas a empresas del territorio preferencial Res. Ex. N° 1057'),
        ('902', '(902) Conocimiento de Embarque (Marítimo o aéreo)'),
        ('903', '(903) Documento Único de Salida (DUS)'),
        ('904', '(904) Factura de Traspaso'),
        ('905', '(905) Factura de Reexpedición'),
        ('906', '(906) Boletas Venta Módulos ZF (todas)'),
        ('907', '(907) Facturas Venta Módulo ZF (todas)'),
        ('911', '(911) Declaración de Ingreso a Zona Franca Primaria'),
        ('914', '(914) Declaración de Ingreso (DIN)'),
        ('919', '(919) Resumen Ventas de nacionales pasajes sin Factura'),
        ('HEM', '(HEM) Hoja de Entrada de Materiales (HEM)'),
        ('HES', '(HES) Hoja de Entrada de Servicio (HES)'),
        ('MIG', '(MIG) Movimiento de Mercancías (MIGO)'),
        ('CHQ', '(CHQ) Cheque'),
        ('PAG', '(PAG) Pagaré'),
    ]

    origin_doc_number = fields.Char(string='Origin Document Number',
                                    help='Origin document number, the document you are referring to', required=True)
    l10n_cl_reference_doc_type_selection = fields.Selection(reference_documents, string='SII Doc Type Selector',
                                                            required=True)
    reason = fields.Char(string='Reason')
    move_id = fields.Many2one('account.move', ondelete='cascade', string='Originating Document')
    date = fields.Date(string='Document Date', required=True)

    def add_invoice_reference(self):
        vals = {
            'origin_doc_number': self.origin_doc_number,
            'l10n_cl_reference_doc_type_selection': self.l10n_cl_reference_doc_type_selection,
            'reason': self.reason,
            'move_id': self.move_id.id,
            'date': self.date
        }
        self.env['l10n_cl.account.invoice.reference'].create(vals)


class AccountMoveInvoiceReferenceDelete(models.TransientModel):
    _name = 'account.move.invoice.reference.delete'
    _description = 'Account Move Invoice Reference Delete'

    move_id = fields.Many2one('l10n_cl.account.invoice.reference', ondelete='cascade', string='Origin Document Number', domain="[('reference_doc_code', '=', False)]")

    #TODO delete invoice reference method
    def delete_invoice_reference(self):
        for rec in self:
            rec.move_id.unlink()
        return True
