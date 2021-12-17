import warnings
from matplotlib import colors
import os, base64, json, requests
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import metrics
from xgboost.sklearn import XGBRegressor
from lightgbm.sklearn import LGBMRegressor
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from mlxtend.regressor import StackingCVRegressor

warnings.filterwarnings('ignore')
# 用以正常显示中文和负号
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号



class Model(object):
    def __init__(self):
        self.csv = './train_dataset.csv'
        self.x_train = None
        self.y_train = None
        self.x_test = None
        self.y_test = None

    def preHandelData(self, scale):
        train = pd.read_csv(self.csv)  # 读入数据
        full = train

        full.reset_index(drop=True, inplace=True)  # 重置索引，以免后续出错
        print(full.corr()['信用分'].sort_values(ascending=False))

        # 重点部分，主办方把缺失值都填充成0，这里还原，后续模型允许空值，所以不乱填充
        # 其实从移动用户年龄好多数据为0这里看也巨奇怪
        full.loc[full['用户年龄'] == 0, '用户年龄'] = None
        full.loc[full['用户话费敏感度'] == 0, '用户话费敏感度'] = None
        full.loc[full['用户账单当月总费用（元）'] == 0, '用户账单当月总费用（元）'] = None  # 当月有通话交往的人
        full.loc[full['用户近6个月平均消费值（元）'] == 0, '用户近6个月平均消费值（元）'] = None

        # 继续观察数据发现数据存在严重拖尾现象，我第一次是用孤立森林删除的，但会表现不好，从训练集分开看，
        # 均存在拖尾现象，这样就先不管，只处理训练集有而测试集没有的异常值
        full.describe([0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 1])  # 小技巧，可以看各个地方的分位数~
        train.describe([0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 1])
        full[full['当月通话交往圈人数'] > 1633]
        full.drop(248, axis=0, inplace=True)
        full['用户话费敏感度'] = full['用户话费敏感度'].fillna(4.0)  # 非拖尾数据，填充众数

        # 分类处理特征，大神说新手可以按特征顺序处理，按离散到连续数据，构造特征好难，就分类看哪个简单先处理哪个
        # 用户信息分为身份特征、消费能力、人脉关系、位置轨迹、应用行为偏好，可以按这个逻辑
        # 简单特征构造就是加减乘除，能想到的都堆上去。。。
        full['话费稳定'] = full['用户账单当月总费用（元）'] / (full['用户当月账户余额（元）'] + 1)  # 有的话费余额为0，+1不会报错
        full['相对6个月平均值稳定'] = full['用户账单当月总费用（元）'] / (full['用户近6个月平均消费值（元）'] + 1)
        full['缴费稳定'] = full['用户账单当月总费用（元）'] / (full['缴费用户最近一次缴费金额（元）'] + 1)
        full['前5个月平均消费值'] = (full['用户近6个月平均消费值（元）'] * 6 - full['用户账单当月总费用（元）']) / 5
        full['当月总费用与前5个月平均值差'] = full['用户账单当月总费用（元）'] - full['前5个月平均消费值']

        # 这里可能有羊毛党数据或者系统工作人员测试账号，加起来这些特征影响应该能放大
        # 其实还构造了各种app次数占比，但是对模型分数提高影响不大，就注掉了，后续再试试
        full['countApp'] = full['当月飞机类应用使用次数'] + full['当月火车类应用使用次数'] + full['当月旅游资讯类应用使用次数'] + full['当月网购类应用使用次数'] + \
                           full[
                               '当月视频播放类应用使用次数'] + full['当月金融理财类应用使用总次数'] + full['当月物流快递类应用使用次数']
        full['交通工具使用次数'] = (full['当月飞机类应用使用次数'] + full['当月火车类应用使用次数'])

        # 参考大神代码，代表现金用户容易缴整十整百金额，网络用户容易缴小数金额，而且可视化之下确实是缴费方式对信用分有影响
        full['缴费方式'] = 0
        full.loc[(full['缴费用户最近一次缴费金额（元）'] != 0) & (full['缴费用户最近一次缴费金额（元）'] % 10 == 0), '缴费方式'] = 1
        full.loc[(full['缴费用户最近一次缴费金额（元）'] != 0) & (full['缴费用户最近一次缴费金额（元）'] % 10 > 0), '缴费方式'] = 2
        full['话费敏感度占比'] = full['用户话费敏感度'].map({1: 0.05, 2: 0.15, 3: 0.15, 4: 0.25, 5: 0.4})

        # 看相关性
        print(full.corr()['信用分'].sort_values(ascending=False))  # 构造特征之后相关性明显提升
        full.drop('用户编码', axis=1, inplace=True)  # 删除无关的编码

        # 分训练集和测试集
        # full = full.dropna()
        train_len = int(50000 * float(scale))
        self.x_train = full.iloc[0:train_len, full.columns != '信用分']
        self.y_train = full.iloc[0:train_len, full.columns == '信用分']
        self.x_test = full.iloc[train_len:, full.columns != '信用分']
        self.y_test = full.iloc[train_len:, full.columns == '信用分']

    def xgboost(self):
        model = XGBRegressor(n_estimators=3000, learning_rate=0.01,
                             max_depth=5, reg_alpha=2.0, reg_lambda=5.0,
                             colsample_bytree=0.5, subsample=0.8,
                             max_leaves=31, min_child_weight=20,
                             tree_method="hist", grow_policy="depthwise",
                             base_score=None)
        print(cross_val_score(model, self.x_train, self.y_train, scoring='neg_mean_absolute_error', cv=3).mean())
        model.fit(self.x_train, self.y_train)
        pred_y = model.predict(self.x_test)
        pred_y = pd.DataFrame(pred_y.round().astype(int))  # 整数格式
        print(metrics.mean_squared_error(self.y_test, pred_y))
        print(metrics.mean_absolute_error(self.y_test, pred_y))

        y_test = self.y_test.reset_index(drop=True)

        plt.plot(pred_y[:99], label=u'predict')
        plt.plot(y_test[:99], label=u'true')
        plt.ylabel(u"信用分")
        plt.title(u"LGBM Model测试前100条")
        plt.legend()
        plt.savefig('cache.png')

        cached_img = open("cache.png")
        cached_img_b64 = base64.b64encode(cached_img.read())
        os.remove("cache.png")
        return cached_img_b64

    def LGBM(self):
        lgb = LGBMRegressor(n_estimators=1968,
                            learning_rate=0.04,
                            max_depth=4,
                            objective='regression_l1',  # 50
                            min_child_samples=50,
                            n_jobs=-1)  # mae14.70
        cross_val_score(lgb, self.x_train, self.y_train, cv=5, scoring='neg_mean_absolute_error').mean()

        # #训练模型，保存结果
        lgb = LGBMRegressor(n_estimators=1968, learning_rate=0.04, max_depth=4, objective='regression_l1'  # 50
                            , min_child_samples=50, n_jobs=-1).fit(self.x_train, self.y_train)
        pred_y = lgb.predict(self.x_test)

        pred_y = pd.DataFrame(pred_y.round().astype(int))  # 按整数格式保存
        # submission = pd.concat([self.test['用户编码'], pred_y], axis=1)
        # submission.columns = ['id', 'score']
        # submission.to_csv(r'./submission1.csv')
        print(metrics.mean_squared_error(self.y_test, pred_y))
        print(metrics.mean_absolute_error(self.y_test, pred_y))

        y_test = self.y_test.reset_index(drop=True)
        plt.plot(pred_y[:99], label=u'predict')
        plt.plot(y_test[:99], label=u'true')
        plt.ylabel(u"信用分")
        plt.title(u"xgboost Model测试前100条")
        plt.legend()
        plt.savefig('save.png')

        cached_img = open("cache.png")
        cached_img_b64 = base64.b64encode(cached_img.read())
        os.remove("cache.png")
        return cached_img_b64

    def xgbAndLGBM(self):
        lr = LinearRegression()
        lgb = LGBMRegressor(n_estimators=3000, learning_rate=0.01,
                            num_leaves=31, max_depth=5, max_bin=255, reg_alpha=2.0,
                            reg_lambda=5.0, colsample_bytree=0.5, subsample=0.8,
                            subsample_freq=2, min_child_samples=20, min_split_gain=1, n_jobs=-1)
        xgb = XGBRegressor(n_estimators=3000, learning_rate=0.01,
                           max_depth=5, reg_alpha=2.0, reg_lambda=5.0,
                           colsample_bytree=0.5, subsample=0.8,
                           max_leaves=31, min_child_weight=20,
                           tree_method="hist", grow_policy="depthwise",
                           base_score=None)
        model_stack = StackingCVRegressor(regressors=(lgb, xgb), meta_regressor=lr)
        print(np.isnan(self.x_train).any())
        model_stack.fit(self.x_train, self.y_train)
        val_stack = model_stack.predict(self.x_test)
        print(metrics.mean_squared_error(self.y_test, val_stack))
        print(metrics.mean_absolute_error(self.y_test, val_stack))

        return 1
        # plt.plot(pred_y[:99], label=u'predict')
        # plt.plot(y_test[:99], label=u'true')
        # plt.ylabel(u"信用分")
        # plt.title(u"xgboost Model测试前100条")
        # plt.legend()
        # plt.save()
        #
        # cached_img = open("cache.png")
        # cached_img_b64 = base64.b64encode(cached_img.read())
        # os.remove("cache.png")
        # return cached_img_b64

    def buildAndFit(self, flag, scale):

        url = "http://localhost:5001/buildandfit"
        headers = {'Content-type': 'application/json'}
        res = {'info': '开始预处理'}
        requests.post(url, data=json.dumps(res), headers=headers)

        self.preHandelData(scale)
        res = {'info': '预处理完成'}

        requests.post(url, data=json.dumps(res), headers=headers)

        res = {'info': '开始训练模型'}
        requests.post(url, data=json.dumps(res), headers=headers)
        if flag == 1:
            info = self.xgboost()
        elif flag == 2:
            info = self.LGBM()
        else:
            info = self.xgbAndLGBM()
        res = {'info': '训练完成，预测结果见右图'}
        requests.post(url, data=json.dumps(res), headers=headers)

        res = {'info': info}
        requests.post(url, data=json.dumps(res), headers=headers)




