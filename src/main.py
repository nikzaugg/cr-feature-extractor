import sys
import os
import subprocess

import pandas as pd
import numpy as np

from code_metrics import extractor as metrics_code
from checkstyle_metrics import extractor as metrics_checkstyle
from pmd_metrics import extractor as metrics_pmd
from ck_metrics import extractor as metrics_ck
from change_metrics import extractor as metrics_change


def main():
    """ Main entry point to compute features for the training-set """

    ## ******************** ##
    ## DATA CREATED BEFORE  ##
    ## ******************** ## 

    ######################################################
    # 1) load ChangeDistiller output for current project #
    ######################################################

    #######################################################
    # 2) load tf-idf matrix of considered commit-messages #
    #######################################################

    ##################################################
    # 3) load Change-Metrics of each considered file #
    ##################################################
    changeData = metrics_change.loadData('acceleo')

    ##############################
    # 4) load preprocess-dataset #
    ##############################
    preprocess_data = pd.read_csv('preprocess_dataset/dataset.csv')

    ############################
    # COMPUTE METRICS FOR FILE #
    ############################
    # list() of list() of features
    feature_rows = list()

    # for each file in preprocess-dataset
    for row in preprocess_data.itertuples():
        feature_row = list()
        code_metrics = dict()
        checkstyle_metrics = dict()
        pmd_metrics = dict()
        ck_metrics = dict()
        change_metrics = dict()

        # list() code-metrics
        # list() checkstyle-metrics
        # list() pmd-metrics
        # list() change-metrics
        # list() tf-idf features
        # list() ck-metrics
        # list() scc-metrics
        # list() labels

        ##################################################################
        # 5) fetch patch of file & fetch patch of previous patchset/base #
        ##################################################################
        fetch_url = row[1]
        project_name = row[2]
        revision_nr = row[5]
        commit_id = row[6]
        ref = row[7]
        file_path = row[9]
        repo_dir = row[10]

        repo_current_loc = repo_dir + '/current-' + project_name + '/'
        repo_previous_loc = repo_dir + '/previous-' + project_name + '/'

        fname_current = repo_current_loc + file_path
        fname_previous = repo_previous_loc + file_path

        f_current_exists = False
        f_previous_exists = False

        # CHECKOUT CURRENT VERSION OF FILE
        print("<=========================== CURRENT ==============================>")
        checkout_ref(repo_current_loc, ref, fetch_url)
        f_current_exists = os.path.isfile(fname_current)
        print("<============= FILE EXISTS ============>", f_current_exists)

        # CHECKOUT PREVIOUS VERSION OF FILE
        patch_nr = ref.split("/")[-1]
        # If current patch is patch nr. 1
        if int(patch_nr) == 1:
            print("<=========================== PREVIOUS ==============================>")
            checkout_prev_file_version(
                repo_previous_loc, file_path, revision_nr)
            f_previous_exists = os.path.isfile(fname_previous)
            print("<============= FILE EXISTS ============>", f_previous_exists)
        # If current patch is not patch nr. 1
        else:
            previous_ref = int(patch_nr) - 1
            new_ref = ref.split("/")[:-1]
            x = ''
            for s in new_ref:
                x = x+s+'/'
            x = x + str(previous_ref)
            print("<=========================== PREVIOUS ==============================>")
            checkout_ref(repo_previous_loc, x, fetch_url)
            f_previous_exists = os.path.isfile(fname_previous)
            print("<============= FILE EXISTS ============>", f_previous_exists)

        ############################################
        # 6) compute Code-Metrics -> save features #
        ############################################
        # code_metrics = metrics_code.extract(fname_current, fname_previous, f_previous_exists)

        ##################################################
        # 7) compute checkstyle-metrics -> save features #
        ##################################################
        # checkstyle_metrics = metrics_checkstyle.extract(fname_current, fname_previous, f_previous_exists)

        ###########################################
        # 8) compute pmd-metrics -> save features #
        ###########################################
        # pmd_metrics = metrics_pmd.extract(fname_current, fname_previous, f_previous_exists)

        ###########################################
        # 9) compute ck-metrics -> save features #
        ###########################################
        # ck_metrics = metrics_ck.extract(fname_current, fname_previous, f_previous_exists)

        #############################################
        # 10) lookup change-metrics -> save features #
        #############################################
        # change_metrics = metrics_change.extract(changeData, row)

        ##########################################
        # 11) lookup tf-idf row -> save features #
        ##########################################

        #####################################################
        # 12) lookup ChangeDistiller types -> save features #
        #####################################################

        ###############################
        # 13) extract labels --> save #
        ###############################

        #########################################
        # 14) add each feature list to features #
        #########################################
        feature_row.append(code_metrics)
        feature_row.append(checkstyle_metrics)
        feature_row.append(pmd_metrics)
        feature_row.append(ck_metrics)
        feature_row.append(change_metrics)

        feature_rows.append(feature_row)

    ##############################################
    # 15) print each feature-row into a data-set #
    ##############################################
    print(len(feature_rows))
    print('> finished analyzing')


def checkout_ref(repoLoc, ref, fetchUrl):
    """ checkout a ref (refs/*/changes/*) of a given repository """
    repository = os.path.dirname(repoLoc)

    git_command = ['git', 'fetch', fetchUrl, ref]
    git_query = subprocess.Popen(git_command, cwd=repository)
    git_query.communicate()

    git_command2 = ['git', 'checkout', 'FETCH_HEAD', '--force']
    git_query2 = subprocess.Popen(git_command2, cwd=repository)
    git_query2.communicate()


def checkout_prev_file_version(repoLoc, filePath, revisionNr):
    """ checkout the previous commit where the given file was last modified of a given repository """
    repository = os.path.dirname(repoLoc)

    git_command = ['git', 'checkout', revisionNr, '--force']
    git_query = subprocess.Popen(git_command, cwd=repository)
    git_query.communicate()

    git_command2 = ['git', 'checkout', 'HEAD^', filePath]
    git_query2 = subprocess.Popen(git_command2, cwd=repository)
    git_query2.communicate()


if __name__ == "__main__":
    main()
