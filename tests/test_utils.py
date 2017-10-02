import os
from unittest import TestCase
import pandas as pd

import etl_utils as util

FIXTURES_BASE_DIR = 'tests/fixtures'


class UtilTest(TestCase):

    def test_roll(self):
        """
        It should return the same DataFrame as the one after a roll_up

        """
        input_df = pd.read_csv(os.path.join(
            FIXTURES_BASE_DIR, 'roll_up_in.csv'))
        res_df = util.roll_up(input_df,
                              levels=['Country', 'Region', 'City'],
                              groupby_vars=['value', 'population'],
                              value_name='Location',
                              var_name='Type')
        res_df = res_df[['Location', 'Type', 'population',
                         'value', 'Country', 'Region', 'City']]
        expected_output = pd.read_csv(
            os.path.join(FIXTURES_BASE_DIR, 'roll_up.csv'))
        self.assertTrue(res_df.equals(expected_output))

    def test_two_values_melt(self):
        """
        It should return the same DataFrame as the expected
        one after a two_values_melt
        """
        input_df = pd.read_csv(os.path.join(
            FIXTURES_BASE_DIR, 'two_values_melt_in.csv'))
        res_df = util.two_values_melt(
            input_df,
            first_value_vars=['avg', 'total'],
            second_value_vars=['evol_avg', 'evol_total'],
            var_name='type',
            value_name='location'
        )

        expected_output = pd.read_csv(os.path.join(
            FIXTURES_BASE_DIR, 'two_values_melt_out.csv'))
        self.assertTrue(res_df.equals(expected_output))

    def test_compute_evolution(self):
        """
        It should compute an evolution column against a period that is distant
        from a fixed offset
        """
        input_df = pd.read_csv(os.path.join(
            FIXTURES_BASE_DIR, 'compute_evolution.csv'))
        evolution_col = util.compute_evolution(
            input_df,
            id_cols=['City', 'Country', 'Region'],
            date_col='Year',
            value_col='population',
            freq=1,
            method='abs',
        )
        self.assertTrue(input_df['evolution'].equals(evolution_col))

        evolution_pct_col = util.compute_evolution(
            input_df,
            id_cols=['City', 'Country', 'Region'],
            date_col='Year',
            value_col='population',
            freq=1,
            method='pct',
        )
        self.assertTrue(input_df['evolution_pct'].equals(evolution_pct_col))

        input_df = pd.read_csv(os.path.join(
            FIXTURES_BASE_DIR, 'compute_evolution.csv'))
        evolution_df = util.compute_evolution(
            input_df,
            id_cols=['City', 'Country', 'Region'],
            date_col='Year',
            value_col='population',
            freq=1,
            method='pct',
            format='df'
        )
        self.assertTrue(
            input_df['populationA-1'].equals(
                evolution_df['population_offseted']))
        self.assertTrue(input_df['evolution_pct'].equals(
            evolution_df['evolution_computed']))
        self.assertEqual(input_df.shape[1] + 2, evolution_df.shape[1])

        evolution_df = util.compute_evolution(
            input_df,
            id_cols=['City', 'Country', 'Region'],
            date_col='Year',
            value_col='population',
            freq=1,
            method='pct',
            format='df',
            offseted_suffix='_A',
            evolution_col_name='evol'
        )
        self.assertTrue(input_df['populationA-1'].equals(
            evolution_df['population_A']))
        self.assertTrue(input_df['evolution_pct'].equals(
            evolution_df['evol']))
        self.assertEqual(input_df.shape[1] + 2, evolution_df.shape[1])

        evolution_df = util.compute_evolution(
            input_df,
            id_cols=['City', 'Country', 'Region'],
            date_col='Date',
            value_col='population',
            freq={
                'years': 1
            },
            method='pct',
            format='df'
        )
        self.assertTrue(input_df['populationA-1'].equals(
            evolution_df['population_offseted']))
        self.assertTrue(input_df['evolution_pct'].equals(
            evolution_df['evolution_computed']))
        self.assertEqual(input_df.shape[1] + 2, evolution_df.shape[1])

        evolution_df = util.compute_evolution(
            input_df,
            id_cols=['City', 'Country', 'Region'],
            date_col='Year',
            value_col='population',
            freq=1,
            method='abs',
            format='df',
            how='outer',
            fillna=0
        )

        evolution_fillna = pd.Series(
            [2, 10, 20, 200, 20, -13, 100, -12, -220, -7, -100])
        self.assertTrue(evolution_df['evolution_computed'].astype(int).equals(
            evolution_fillna))
        self.assertEqual(11, evolution_df.shape[0])
        self.assertEqual(input_df.shape[1] + 2, evolution_df.shape[1])

    def test_compute_cumsum(self):
        """
        It should compute cumsum
        """
        input_df = pd.read_csv(os.path.join(
            FIXTURES_BASE_DIR, 'compute_cumsum.csv'))
        cumsum_df = util.compute_cumsum(
            input_df,
            id_cols=['City', 'Country', 'Region'],
            reference_cols=['Date'],
            value_cols=['population']
        )
        self.assertTrue(input_df['population_cumsum'].equals(
            cumsum_df['population']))

        cumsum_df = util.compute_cumsum(
            input_df,
            id_cols=['City', 'Country', 'Region'],
            reference_cols=['Date'],
            value_cols=['population'],
            cols_to_keep=['blob']
        )
        self.assertTrue(input_df['blob'].equals(cumsum_df['blob']))

    def test_add_missing_row(self):
        """
        It should add missing row compare to a reference column
        """
        input_df = pd.read_csv(os.path.join(
            FIXTURES_BASE_DIR, 'add_missing_row.csv'))
        new_df = util.add_missing_row(
            input_df,
            id_cols=['City', 'Country', 'Region'],
            reference_col='Year'
        )
        self.assertEqual(new_df.shape[0], 12)

    def test_add_missing_row_use_index(self):
        """
        It should add missing row using the index provided
        """
        input_df = pd.read_csv(os.path.join(
            FIXTURES_BASE_DIR, 'add_missing_row.csv'))
        new_df = util.add_missing_row(
            input_df,
            id_cols=['City', 'Country', 'Region'],
            reference_col='Year',
            complete_index=['2009', '2010', '2011', '2012']
        )
        self.assertEqual(new_df.shape[0], 16)

    def test_compute_ffill_by_group(self):
        """
        It should compute ffill with a groupby
        """
        input_df = pd.read_csv(os.path.join(
            FIXTURES_BASE_DIR, 'compute_ffill_by_group.csv'))
        new_df = util.compute_ffill_by_group(
            input_df,
            id_cols=['City', 'Country', 'Region'],
            reference_cols=['Year'],
            value_col='population',
        )

        conditions = [
            {'Year': 2011, 'City': 'Lille', 'ffilled': True},
            {'Year': 2010, 'City': 'Nantes', 'ffilled': False},
            {'Year': 2012, 'City': 'Nantes', 'ffilled': True},
            {'Year': 2010, 'City': 'Paris', 'ffilled': False},
        ]

        for cond in conditions:
            self.assertEqual(
                new_df.loc[(new_df['Year'] == cond['Year']) &
                           (new_df['City'] == cond['City']),
                           'population'].notnull().all(),
                cond['ffilled'])
