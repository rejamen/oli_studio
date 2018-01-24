# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Solucións Aloxa S.L. <info@aloxa.eu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
{
    'name': "oli_recepcion",

    'summary': """
        Control de Trabajos.""",

    'description': """
        Controla lo relacionado con los trabajos realizados en el estudio.
    """,

    'author': "OliStudio",
    'website': "http://www.olistudio.com",

    'version': '0.1',

    'depends': ['base', 'oli_almacen'],

    # always loaded
    'data': [
        'wizard/wizard.xml',
        'views/recepcion.xml',
        'report/contrato_report.xml',
        'oli_recepcion_report.xml',
        'trabajo.xml',
        'predefinida.xml',
        'predefinida_data.xml',
        'tasa_cambiaria_data.xml',
        'tasa_cambiaria.xml',
        'balance_diario.xml',
        'balance_semanal.xml',
        'encargo.xml',
        'nota.xml',

    ],
    # only loaded in demonstration mode
    'demo': [        
    ],
    "installable": True,
}