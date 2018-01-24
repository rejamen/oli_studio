# -*- coding: utf-8 -*-
from openerp import models, fields, api
import os, sys
from openerp.osv import osv
from openerp.tools.translate import _

class tasa_cambiaria(models.Model):
    _name='tasa.cambiaria'

    cup = fields.Integer('CUP', help="Indica la equivalencia en CUP de 1 CUC")

    def unlink(self, cr, uid, ids, context=None):
    	raise osv.except_osv(_('Error!'),_("No se puede eliminar la tasa de cambio, solo puede modificarla."))

