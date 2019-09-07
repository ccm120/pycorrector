import operator
from pycorrector.utils.text_utils import uniform, is_alphabet_string
from pycorrector.tokenizer import Tokenizer
from pycorrector.detector import Detector
from pycorrector import config
from pycorrector import ccm_conf
import codecs

PUNCTUATION_LIST = ".。,，,、?？:：;；{}[]【】“‘’”《》/!！%……（）<>@#$~^￥%&*\"\'=+-_——「」"
LINK_WORD = ['转达', '传达', '表示', '说', '指出']


class NameSort(object):

    def __init__(self, word_freq_path=config.word_freq_path, name_sort_path=ccm_conf.name_sort_path,
                 leader_job_path=ccm_conf.leader_job_path,
                 leader_job_freq_dict_path=ccm_conf.leader_job_freq_dict_path):
        self.leader_job_freq_dict = Detector.load_word_freq_dict(leader_job_freq_dict_path)
        self.word_freq_path = word_freq_path
        print(self.leader_job_freq_dict)
        self.tokenizer = Tokenizer(dict_path=self.word_freq_path, custom_word_freq_dict=self.leader_job_freq_dict)
        self.name_sort_path = name_sort_path
        self.leader_job_path = leader_job_path

    def is_filter_token(self, token):
        result = False
        # pass blank
        if not token.strip():
            result = True
        # pass punctuation
        if token in PUNCTUATION_LIST:
            result = True
        # pass num
        if token.isdigit():
            result = True
        # pass alpha
        if is_alphabet_string(token.lower()):
            result = True
        return result

    def load_ccm_word_freq_dict(self, path):
        """
        加载切词词典
        :param path:
        :return:
        """
        word_freq = {}
        with codecs.open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    continue
                info = line.split('+')
                if len(info) < 1:
                    continue
                word = info[0]  # word为姓名
                # 取词频，默认1 长度大于一时 freq=info[1]为顺序 否则定义为1
                freq = int(info[1]) if len(info) > 1 else 1
                word_freq[word] = freq
            # print("++++" + str(word_freq))
        return word_freq

    def load_ccm_job_freq_dict(self, path):
        """
        加载切词词典
        :param path:
        :return:
        """
        word_freq = {}
        with codecs.open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                info = line.split('：')
                if len(info) < 1:
                    continue
                # print("dddddd")
                word = info[0]  # 名字-习近平
                # print(word)
                job = info[1]  # 职务+称谓
                # print(job)
                s1 = job.split('？')
                if len(s1) > 1:
                    # print(s1)
                    s2 = s1[0].split('、')  # 将职务用、隔开
                    s3 = s1[1].split('、')  # 将称谓用、隔开
                    # print(s2)
                    # print(s3)
                    b = {'1': s2, '2': s3}
                else:
                    s2 = s1[0].split('、')  # 将职务用、隔开
                    b = {'1': s2}
                # 取词频，默认1
                # freq = int(info[1]) if len(info) > 1 else 1
                word_freq[word] = b
        return word_freq

    def ccm_sort(self, sentence):
        """
        """
        # 加载排序词典
        name_model = self.load_ccm_word_freq_dict(self.name_sort_path)
        maybe_errors = []
        if not sentence.strip():
            return maybe_errors
        # 文本归一化
        sentence = uniform(sentence)
        # 切词
        tokens = self.tokenizer.tokenize(sentence)
        print(tokens)
        temp = None
        error_list = []
        correct_list = []
        new = []
        i = -1
        for word, begin_idx, end_idx in tokens:
            new.append(word)
            i += 1
            if word in LINK_WORD:
                temp = None
            if name_model.get(word):
                if not temp:
                    temp = name_model.get(word)
                    continue
                else:
                    if temp > name_model.get(word):
                        p = tokens[i]
                        tokens[i] = tokens[i - 2]
                        tokens[i - 2] = p
                        print(tokens[i][0])
                        print(tokens[i - 2][0])
                        correct_list.append((tokens[i][0], i))
                        correct_list.append((tokens[i - 2][0], i - 2))
                        error_list.append((tokens[i][0], i))
                    else:
                        pass
            # print(tokens)
        # correct_list.append((tokens[i][0]))
        for word, p in correct_list:
            new[p] = word
        print(new)
        print("ls:" + str(correct_list))
        correct = ''.join(new)
        print("correct:" + correct)
        # print(error_list)

        # print(tokens)
        # print(tokens[0])

        return sorted(maybe_errors, key=lambda k: k[1], reverse=False)

    def name_job(self, sentence):
        """
        """
        # 加载人名-职务词典
        job_model = self.load_ccm_job_freq_dict(self.leader_job_path)
        print(job_model)
        maybe_errors = []
        if not sentence.strip():
            return maybe_errors
        # 文本归一化
        sentence = uniform(sentence)
        # 切词
        tokens = self.tokenizer.tokenize(sentence)
        print(tokens)
        # temp = None
        error_list = []
        correct_list = []
        new = []
        i = 0
        j = 0
        for word, begin_idx, end_idx in tokens:
            if job_model.get(word):
                print(i)  # 如果找到人名了，那么现在的i就是该人名的坐标
                a = job_model.get(word)
                front = a.get('1')
                temp_list = []
                for x in range(j, i):  # j就是起点坐标，i就是终点坐标
                    if self.leader_job_freq_dict.get(tokens[x][0]):
                        if tokens[x][0] not in front:
                            temp_list.append(tokens[x][0])
                if temp_list:
                    error_list.append({word: temp_list})
                else:
                    pass
                j = i+1  # 起点坐标变为上一个人坐标的下一位坐标
            i += 1
        print(error_list)




a = '李鸿忠转达赵乐际和习近平对普京总统的亲切问候'
c = '国务院总理哈哈哈中共中央政治局常委、中央精神文明建设指导委员会办公室主任习近平出席了会议中央精神文明建设指导委员会办公室主任李克强'
name_sort = NameSort()
# name_sort.ccm_sort(a)
name_sort.name_job(c)
# a=name_sort.load_ccm_word_freq_dict(name_sort_path)
# print(a)
