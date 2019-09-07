import os

pwd_path = os.path.abspath(os.path.dirname(__file__))
# 领导人排序
name_sort_path = os.path.join(pwd_path, 'data/LSQLIB.txt')
leader_job_path = os.path.join(pwd_path, 'data/LNDLIB.txt')
quotation_word_path = os.path.join(pwd_path, 'data/QTLIB.txt')
leader_job_freq_dict_path = os.path.join(pwd_path, 'data/leader_job_freq.txt')
