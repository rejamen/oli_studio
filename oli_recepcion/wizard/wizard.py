# -*- coding: utf-8 -*-
from openerp import models, fields, api
import os, sys
from openerp.osv import osv
from openerp.tools.translate import _
from datetime import datetime,date

class realizar_pago_wizard(models.TransientModel):
    _name="realizar.pago.wizard"


    @api.model
    def default_get(self, fields_list):
        origen = self.env['encargo.encargo'].search([(
            'id','in',self.env.context.get('active_ids',[]))])
        res = models.TransientModel.default_get(self, fields_list)
        ids = self.env.context.get('active_ids', [])
        pagos = self.env['pagos.encargo.line'].browse(ids)
        wizard_obj = self.env['realizar.pago.wizard.lines']
        ds = []
        debe = 0
        for pago in origen.pagos_line:
            if pago.state == 'draft':
                d = wizard_obj.create({
                    'wizard_id': self.id,
                    'fecha': pago.fecha,
                    'importe': pago.importe,
                    'pago_line_id': pago.id,
                    })
                ds.append(d.id)
                debe += pago.importe

        res['cliente_id'] = origen.cliente_id.id
        res['importe_pendiente'] = debe
        res['pagos_line'] = ds
        
        return res

    def pagar(self, cr, uid, ids, context=None):
        for e in self.browse(cr, uid, ids, context=None):
            wizard_line_obj = self.pool.get('realizar.pago.wizard.lines')
            trabajo_obj = self.pool.get('trabajo.trabajo')

            wizard_ids = wizard_line_obj.search(cr, uid, [('select','=',True),('wizard_id','=', e.encargo_origen_id.id)])
            if not wizard_ids:
                raise osv.except_osv(_('Error!'),_("Seleccione al menos un pago a realizar."))
            
            
            if wizard_ids:
            	pagos_line_obj = self.pool.get('pagos.encargo.line')
                for w in wizard_ids:
                    wid = wizard_line_obj.browse(cr, uid, w, context=context)
                    pagos_line_obj.write(cr, uid, wid.pago_line_id.id, {'state': 'done'})
                    #crear un trabajo
                    # trabajo_obj = self.pool.get('trabajo.trabajo')
                    # predef_ob = self.pool.get('predefinida.predefinida')
                    # predef_id = predef_ob.search(cr, uid, [('name','=','Pago parcial trabajo por encargo')])
                    # total = wid.importe
                    # cliente_id = e.encargo_origen_id.cliente_id.id
                    # vals = {
                    #     'costo': total,
                    #     'cliente': cliente_id,
                    #     'name': predef_id[0],
                    #     }
                    # nid = trabajo_obj.create(cr, uid, vals)


        # #eliminar los transientModels creados
        # wizard_obj = self.pool.get('realizar.pago.wizard')
        # wizard_ids = wizard_obj.search(cr, uid, [])
        # for w in wizard_ids:
        #     wizard = wizard_obj.browse(cr, uid, w)
        #     wizard.unlink()

        return True

    encargo_origen_id = fields.Many2one('encargo.encargo', 'Encargo', help="Encargo al que pertenecen los pagos a realizar.")
    cliente_id = fields.Many2one('cliente.cliente', 'Cliente')
    fecha = fields.Date('Fecha', help="Fecha en la que se realiza el pago. No necesariamente tiene que coincidir con las fechas indicadas en la linea de pagos pendientes. Al realizar el pago, se registrara un trabajo cuya fecha coincide con la especificada en este campo.")
    importe_pendiente = fields.Float('Importe pendiente (MN)')
    pagos_line = fields.One2many('realizar.pago.wizard.lines', 'wizard_id', 'Pagos line')

    _defaults={
        'fecha': fields.Date.today,
    }

class realizar_pago_wizard_lines(models.TransientModel):

    _name='realizar.pago.wizard.lines'

    wizard_id = fields.Many2one('realizar.pago.wizard', 'Encargo', select=True, ondelete='cascade')
    pago_line_id = fields.Many2one('pagos.encargo.line','Pago')
    select = fields.Boolean('Pago', help="Marque para seleccionar este pago")
    fecha = fields.Date('Fecha')
    importe = fields.Float('Importe')
