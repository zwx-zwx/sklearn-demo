import numpy as np
from sklearn.utils import Bunch
from clickhouse_driver import Client
# 将数据分为测试集和训练集
from sklearn.model_selection import train_test_split
# 利用邻近点方式训练数据
from sklearn.neighbors import KNeighborsClassifier

class DB_Obj(object):
    def __init__(self, db_name):
        self.db_name = db_name
        self.host = "122.9.150.90"
        self.port = "9000"
        self.database = db_name
        self.send_receive_timeout = 25
        self.settings = {'max_block_size': 10000}
        self.client = Client(host=self.host, port=self.port, database=self.database)

    def showDatabases(self):
        data = self.client.execute(
            "show databases"
            )
        print(f"db server: {self.host}:{self.port} has databases:", data)

    def desc(self, table):
        tableDesc = self.client.execute(f"desc ({table})")
        res = list()
        for col in tableDesc:
            res.append(col[0])
        return res

    def do(self, query_sql):
        dataset = self.client.execute(query_sql)
        res=list()
        for data in dataset:
            res.append(list(data))
        return res


def load_rbb(dataset):
    rbb=Bunch()
    rbb.data = _get_rbbdata(dataset)
    rbb.target = _get_rbbtarget(dataset)
    return rbb


def _get_rbbdata(dataset):
    return np.array(dataset[:, 1:-1])


def _get_rbbtarget(dataset):
    return np.array(dataset[:, -1])


def getModel(query):
    dataset = np.array(db_obj.do(query))
    bunch = load_rbb(dataset)
    X = bunch.data
    y = bunch.target
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    knn = KNeighborsClassifier()
    knn.fit(X_train, y_train)
    score = knn.score(X_test, y_test)
    print(f"預測分數為：{score}")
    return knn


def predict_star():
    star_query = """
            select
                *
            from star_dataset
            where star_level!='-1'
                """
    star_query_1 = """
            select
                *
            from star_dataset
            where star_level='-1'
        """
    knn_star = getModel(star_query)
    p = np.array(db_obj.do(star_query_1))
    p_y = knn_star.predict(p[:, 1:-1])
    for i in range(len(p)):
        p[i][-1] = p_y[i]
    p = p[:, [0, -1]]
    np.savetxt("39_star.csv", p, fmt='%s')


def predict_credit():
    credit_query = """
        select
            c.uid uid,
            l.all_bal all_bal,
            l.bad_bal bad_bal,
            l.due_intr due_intr,
            l.norm_bal norm_bal,
            l.delay_bal delay_bal,
            c.credit_level credit_level
        from pri_credit_info c
        left join pri_cust_liab_info l on c.uid=l.uid 
        where c.credit_level!='-1'
        """
    credit_query_1 = """
            select
                c.uid uid,
                l.all_bal all_bal,
                l.bad_bal bad_bal,
                l.due_intr due_intr,
                l.norm_bal norm_bal,
                l.delay_bal delay_bal,
                c.credit_level credit_level
            from pri_credit_info c
            left join pri_cust_liab_info l on c.uid=l.uid 
            where c.credit_level='-1'
        """
    knn = getModel(credit_query)
    p = np.array(db_obj.do(credit_query_1))
    p_y = knn.predict(p[:, 1:-1])
    for i in range(len(p)):
        p[i][-1] = p_y[i]
    p = p[:, [0, -1]]
    np.savetxt("39_credit.csv", p, fmt='%s')


if __name__ == '__main__':
    db_obj = DB_Obj("dm")
    # db_obj.showDatabases()
    # print(db_obj.desc("pri_star_info"))
    # test = """
    #     select * from pri_star_info
    # """
    # print(db_obj.desc(test))

    predict_star()
    predict_credit()




