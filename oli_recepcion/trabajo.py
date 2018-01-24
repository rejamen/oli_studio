# -*- coding: utf-8 -*-
from openerp import models, fields, api
import os, sys
from openerp.osv import osv
from openerp.tools.translate import _



class trabajo_trabajo(models.Model):
    _name = 'trabajo.trabajo'

    def name_get(self, cr, uid, ids, context=None):
	  	res = []
	  	for e in self.browse(cr,uid, ids, context=context):
	  		name = e.name
	  		res.append((e['id'],name))
	  	return res

    @api.depends('costo','unidades')
    def _get_importe(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            tasa_obj = self.pool.get('tasa.cambiaria')
            tasa_ids = tasa_obj.search(cr, uid, [])
            tasa_id = tasa_obj.browse(cr, uid, tasa_ids[0])
            costo = record.costo * record.unidades
            cuc = costo/tasa_id.cup
            record.update({'importe_mn': costo, 'importe_cuc': cuc})

    @api.depends('materiales_line')
    def _get_costo(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            costo = 0
            if record.materiales_line:
                for m in record.materiales_line:
                    costo += m.costo
            record.update({'costo_materiales': costo})

    def onchange_name(self, cr, uid, ids, name, context=None):
        result = {}
        if name:
            name_id = self.pool.get('predefinida.predefinida').browse(cr, uid, name)
            result['costo'] = name_id.costo
            result['control_stock'] = name_id.control_stock
        return {'value': result}

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for e in self.browse(cr,uid, ids, context=context):
            name = e.name.name
            res.append((e['id'],name))
        return res

    def _get_user(self, cr, uid, ids, context=None):
        return uid
        

    name = fields.Many2one('predefinida.predefinida', 'Nombre')
    unidades = fields.Integer('Unidades', default=1, help="Indica la cantidad de unidades de este trabajo. Por ejemplo, en un trabajo de impresion, este dato representa la cantidad de hojas impresas.")
    costo = fields.Float('Costo (MN)', required=True)
    
    importe_mn = fields.Float('Importe (MN)', compute="_get_importe")
    importe_cuc = fields.Float('Importe (CUC)', compute="_get_importe")

    control_stock = fields.Boolean('Control stock', help="Si esta marcado significa que para este trabajo es obligatorio controlar el stock. Es decir, si fuera un trabajo de impresion es necesario controlar la cantidad de hojas utilizadas.")
    cliente = fields.Many2one('cliente.cliente', 'Cliente')

    materiales_line = fields.One2many('materiales.trabajo.line', 'trabajo_id', 'Materiales Line')
    costo_materiales = fields.Float('Costo (MN)', compute="_get_costo")

    notas_line = fields.One2many('notas.trabajo.line', 'trabajo_id', 'Notas Line')

    propina = fields.Boolean('Propina')
    total_propina = fields.Float('Total propina')


    tipo_trabajo = fields.Selection([
        ('momento', 'Al momento'),
        ('encargo', 'Encargo'),
        ], 'Tipo trabajo', default='momento')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Pagado'),
        ], 'Estado', default='draft')

    fecha = fields.Date('Fecha', help="Fecha en que se realiza el trabajo.")

    user_id = fields.Many2one('res.users', 'Usuario')

    _defaults={
        'fecha': fields.Date.today,
        'user_id': _get_user,
    }

    _order="fecha desc"

class materiales_trabajo_line(models.Model):
    _name="materiales.trabajo.line"

    @api.depends('producto_id')
    def _get_costo(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.producto_id:
                producto_obj = self.pool.get('producto.producto')
                producto_id = producto_obj.browse(cr, uid, record.producto_id.id)
                costo = record.cantidad * producto_id.costo
                record.update({'costo': costo})


    trabajo_id = fields.Many2one('trabajo.trabajo', 'Trabajo',  select=True, ondelete='cascade')
    producto_id = fields.Many2one('producto.producto', 'Producto', domain=[('ubicacion', '=', 'diario')])
    cantidad = fields.Integer('Cantidad')
    costo = fields.Float('Costo (MN)', compute="_get_costo")

class notas_trabajo_line(models.Model):
    _name="notas.trabajo.line"

    trabajo_id = fields.Many2one('trabajo.trabajo', 'Trabajo',  select=True, ondelete='cascade')
    name = fields.Char('Nota')

class tasa_cambiaria(models.Model):
    _name='tasa.cambiaria'

    cup = fields.Integer('CUP', help="Indica la equivalencia en CUP de 1 CUC")
