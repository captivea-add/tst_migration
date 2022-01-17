from odoo import models, fields
from odoo.tests import common, tagged


class TestDuplicateCommon(common.TransactionCase):

    def setUp(self):
        super(TestDuplicateCommon, self).setUp()
        self.wizard_id = self.env['wizard.several.copy'].create({'number_of_copy': 1})


@tagged('-standard', 'captivea', 'at_install')
class test_duplicate(TestDuplicateCommon):

    def test_wizard_default_value(self):
        self.assertEqual(self.wizard_id.number_of_copy, 1)

    def test_duplicate_1_record_1_time(self):
        record_to_duplicate = self.env['mock.test.duplicate'].create({'name': 'record_1'})
        domain = [('name', '=', 'record_1')]

        nb_records = self.env['mock.test.duplicate'].search_count(domain)
        self.assertEqual(nb_records, 1)

        self.wizard_id.with_context(active_model=record_to_duplicate._name,
                                    active_ids=[record_to_duplicate.id]).copy_several_times()

        nb_records = self.env['mock.test.duplicate'].search_count(domain)
        self.assertEqual(nb_records, 2)

    def test_duplicate_1_record_N_times(self):
        record_to_duplicate = self.env['mock.test.duplicate'].create({'name': 'record_1'})
        domain = [('name', '=', 'record_1')]

        nb_records = self.env['mock.test.duplicate'].search_count(domain)
        self.assertEqual(nb_records, 1)

        self.wizard_id.number_of_copy = 5
        self.wizard_id.with_context(active_model=record_to_duplicate._name,
                                    active_ids=[record_to_duplicate.id]).copy_several_times()

        nb_records = self.env['mock.test.duplicate'].search_count(domain)
        self.assertEqual(nb_records, self.wizard_id.number_of_copy+1)

    def test_duplicate_N_records_1_time(self):
        records_to_duplicate = self.env['mock.test.duplicate']
        records_to_duplicate += records_to_duplicate.create({'name': 'record_1'})
        records_to_duplicate += records_to_duplicate.create({'name': 'record_2'})
        domain = [('name', 'in', ['record_1', 'record_2'])]

        nb_records = self.env['mock.test.duplicate'].search_count(domain)
        self.assertEqual(nb_records, 2)

        self.wizard_id.with_context(active_model=records_to_duplicate._name,
                                    active_ids=records_to_duplicate.ids).copy_several_times()

        nb_records = self.env['mock.test.duplicate'].search_count(domain)
        self.assertEqual(nb_records, 4)

    def test_duplicate_N_records_N_times(self):
        records_to_duplicate = self.env['mock.test.duplicate']
        records_to_duplicate += records_to_duplicate.create({'name': 'record_1'})
        records_to_duplicate += records_to_duplicate.create({'name': 'record_2'})
        domain = [('name', 'in', ['record_1', 'record_2'])]

        nb_records = self.env['mock.test.duplicate'].search_count(domain)
        self.assertEqual(nb_records, 2)

        self.wizard_id.number_of_copy = 5
        self.wizard_id.with_context(active_model=records_to_duplicate._name,
                                    active_ids=records_to_duplicate.ids).copy_several_times()

        nb_records = self.env['mock.test.duplicate'].search_count(domain)
        self.assertEqual(nb_records, 2*(self.wizard_id.number_of_copy+1))


class MockTestDuplicate(models.Model):
    """ This model is used for unit testing duplication """
    _description = 'Mock Test Duplicate'
    _name = 'mock.test.duplicate'
    _inherit = ['model.several.copy']

    name = fields.Char()
