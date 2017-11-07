#!/usr/bin/env python
'''
Run test of tRep
'''

import os
import glob
import pandas as pd

import tRep

def load_b6_loc():
    return os.path.join(str(os.getcwd()) + \
        '/testFiles/N1_003_000G1_scaffold_min1000.fa.genes.faa-vs-uniprot.b6+')

def load_ggkbase_loc():
    return os.path.join(str(os.getcwd()) + \
        '/testFiles/N1_003_000G1.contig-taxonomy.tsv')

def load_ggkbase_org_table():
    return os.path.join(str(os.getcwd()) + \
        '/testFiles/N1_003_000G1.organism_info.tsv')

def load_sample_Tdb():
    return os.path.join(str(os.getcwd()) + \
        '/testFiles/Tdb.csv')

def load_sample_s2b_loc():
    return os.path.join(str(os.getcwd()) + \
        '/testFiles/N1_003.delta.stb')

class testUniProt():
    def setUp(self):
        self.b6_loc = load_b6_loc()
        self.ggkbase_s2t_loc = load_ggkbase_loc()

    def tearDown(self):
        pass

    def run(self):
        self.setUp()
        self.main_test_1()
        self.main_test_2()
        self.main_test_3()
        self.main_test_4()
        self.tearDown()

    def main_test_1(self):
        '''
        test loading b6 file and running on large amounts of data
        '''
        Bdb = tRep.load_b6(self.b6_loc)
        Bdb = Bdb[Bdb['taxID'] != 'NA']
        tax = tRep.gen_taxonomy_string(Bdb['taxID'].tolist())
        assert tax == '1239|Bacteria|Firmicutes|unk|unk|unk|unk|unk'

    def main_test_2(self):
        '''
        test gen_levels_db (making Tdb)
        '''
        # Load Bdb
        Bdb = tRep.load_b6(self.b6_loc)
        Bdb = Bdb[Bdb['taxID'] != 'NA']
        Gdb = pd.read_table(self.ggkbase_s2t_loc)

        # Add the taxonomy
        tax = tRep.gen_levels_db(list(Bdb['taxID'].unique()))
        Tdb = pd.merge(Bdb, tax, on='taxID', how='outer')
        assert len(Tdb) == len(Bdb)


    def main_test_3(self):
        '''
        Make scaffold level taxonomy calls; compare to ggkbase taxonomy calls
        '''
        Tdb = pd.read_csv(load_sample_Tdb())
        Gdb = pd.read_table(self.ggkbase_s2t_loc)

        # Generate scaffold2taxonomy
        Sdb = tRep.gen_taxonomy_table(Tdb, on='scaffold')

        # compare genus-level calls = make sure at least half are the same
        for level in ['genus']:#, 'species']:
            s_col = level + '_winner'
            g_col = level[0].upper() + level[1:] + ' winner'

            s2t = Sdb.set_index('scaffold')[s_col].to_dict()
            Gdb[s_col] = Gdb['Contig name'].map(s2t)
            tdb = Gdb[Gdb[s_col] != Gdb[g_col]]
            assert len(tdb)/len(Gdb) < .5

    def main_test_4(self):
        '''
        Test generating taxonomy based on scaffold 2 bin file
        '''
        Tdb = pd.read_csv(load_sample_Tdb())
        stb = tRep.load_stb(load_sample_s2b_loc())

        # Add the bin to Tdb
        Tdb = tRep.add_bin_to_tdb(Tdb, load_sample_s2b_loc())
        Tdb['bin'] = ['N1_003_000G1_UNK' if x == 'unk' else x.replace('.', '_') \
            for x in Tdb['bin']]

        # Load ggkbase org table
        Gdb = pd.read_table(load_ggkbase_org_table())

        # Make sure the ggkbase org table and my table have the same bins
        assert len(Gdb['name'].unique()) == len(Tdb['bin'].unique())
        for org in Gdb['name'].unique():
            assert org in Tdb['bin'].tolist(), org

        # Make Sdb
        Sdb = tRep.gen_taxonomy_table(Tdb, on='bin')

        # Make sure Sdb and ggkbase get the same taxonomy
        Gdb['new_tax'] = Gdb['name'].map(Sdb.set_index('bin')['taxonomy'].to_dict())
        db = Gdb[['new_tax', 'name', 'taxonomy']]
        for i, row in db.iterrows():
            if (row['name'] in ['N1_003_000G1_UNK', 'dasN1_003_000G1_concoct_26_fa']):
                continue

            my_tax = row['new_tax'].split('|')[-1]
            gg_tax = row['taxonomy'].split(',')[0]

            assert my_tax == gg_tax
        # # Make sure the ggkbase org table and my table have the same bin characteristics
        # for org, db in Tdb.groupby('bin'):
        #     scaffolds = len(db['scaffold'].unique())
        #     features = len(db)
        #
        #     gg_scaffolds = int(Gdb['# contigs'][Gdb['name'] == org].tolist()[0])
        #     gg_features = int(Gdb['# features'][Gdb['name'] == org].tolist()[0])
        #
        #     print("{0} {1}".format(features, gg_features))
        #
        #     # print(org)
        #     # gg_scaffolds = int(Gdb['# contigs'][Gdb['name'] == org].tolist()[0])
        #     # print("{0} {1}".format(scaffolds, gg_scaffolds))
        #     # # assert scaffolds == gg_scaffolds, \
        #     # #     str(scaffolds) + '_' + str(gg_scaffolds)
        #     #
        #     # if org == 'dasN1_003_000G1_maxbin2_maxbin_009_fasta_fa':
        #     #     scaffs = [k for k,v in stb.items() if v == 'dasN1_003_000G1_maxbin2.maxbin.009.fasta.fa']
        #     #     for scaff in scaffs:
        #     #         if scaff not in db['scaffold'].tolist():
        #     #             print(scaff)

class testMakeTdb():
    pass


if __name__ == '__main__':
    testUniProt().run()
    print('everything is working swimmingly!')
