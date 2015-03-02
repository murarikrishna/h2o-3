import unittest, random, sys, time
sys.path.extend(['.','..','../..','py'])
import h2o2 as h2o
import h2o_browse as h2b, h2o_exec as h2e, h2o_import as h2i, h2o_gbm
import h2o_print as h2p

class Basic(unittest.TestCase):
    def tearDown(self):
        h2o.check_sandbox_for_errors()

    @classmethod
    def setUpClass(cls):
        global SEED
        SEED = h2o.setup_random_seed()
        h2o.init(1, java_heap_GB=12, base_port=54333)

    @classmethod
    def tearDownClass(cls):
        h2o.tear_down_cloud()

    def test_rapids_cbind_vec(self):

        bucket = 'smalldata'
        csvPathname = 'iris/iris_wheader.csv'
        hexKey = 'r1'
        parseResult = h2i.import_parse(bucket=bucket, path=csvPathname, schema='put', hex_key=hexKey)

        keys = []
        # stop if > 1G (fails memory cleaner assetion
        maxx = 29
        # for trial in range(maxx):
        # for trial in range(int(1e6),int(200e6),int(1e6)):
        for trial in [int(100e6)]:
            
            # length = (2 ** trial)
            # execExpr = '(= !v (c {(: #0 #%s)})' % (length - 1)
            length = trial
            execExpr = '(= !v (c {(: #0 #%s)})' % (length - 1)
    
            start = time.time()
            execResult, result = h2e.exec_expr(h2o.nodes[0], execExpr, resultKey=None, timeoutSecs=10)
            elapsed1 = time.time() - start
            if execResult['num_rows']:
                keys.append(execExpr)

            # execExpr = '(= !v (+ (+ %v %v) (+ %v %v))'
            # cols = 100
            xList = []
            eList = []
            fList = []
            for trial2 in range(0, 16):
            # for trial2 in range(0, 10):
            # fails. Post size?
            # for trial2 in range(0, 16):
                col = 2 ** trial2
                # assert col < 16384, "h2o can't take col == 16384 or more"
             
                vString = ' '.join(['%v' for x in range(col)])
                execExpr = '(= !v2 (cbind %s))' % vString

                # FIX! check the colnames. 2 cols get C1 and C10? odd 
                # try:
                start = time.time()
                execResult, result = h2e.exec_expr(h2o.nodes[0], execExpr, resultKey=None, timeoutSecs=40)
                elapsed2 = time.time() - start

                if execResult['num_rows']:
                    keys.append(execExpr)
                
                # except:
                #     elapsed2 = 0
                #     h2p.red_print("ERROR: col = %s failed" % col)

                if 1==0:
                    start = time.time()
                    execExpr = '(sum %v2 %TRUE)'
                    execResult, result = h2e.exec_expr(h2o.nodes[0], execExpr, resultKey=None, timeoutSecs=60)
                    elapsed1 = time.time() - start

                # xList.append(length)
                xList.append(col)
                eList.append(elapsed1)
                fList.append(elapsed2)


        if 1==1:
            xLabel = 'col'
            eLabel = 'elapsed (sum)'
            fLabel = 'elapsed (cbind cols)'
            eListTitle = ""
            fListTitle = ""
            h2o_gbm.plotLists(xList, xLabel, eListTitle, eList, eLabel, fListTitle, fList, fLabel)



        print "\nExpressions that created keys"
        for k in keys:
            print k

        # for execExpr in exprList:
        #     h2e.exec_expr(execExpr=execExpr, resultKey=None, timeoutSecs=10)

        h2o.check_sandbox_for_errors()


if __name__ == '__main__':
    h2o.unit_main()
