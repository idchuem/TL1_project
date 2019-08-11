class OsrpNode():

    def __init__(self):
        self.links=[
            {'id': 1, 'port': 'A-1-1', 'capacity': 'OTU4e', 'dest': 'Node-B', 'status': 'normal' }
            , {'id': 2, 'port': 'A-1-2', 'capacity': 'OTU4e', 'dest': 'Node-C', 'status': 'normal' }
            , {'id': 3 'port': 'A-2-1', 'capacity': 'OTU4e', 'dest': 'Node-D', 'status': 'normal' }
            , {'id': 4 'port': 'A-2-2', 'capacity': 'OTU4e', 'dest': 'Node-B', 'status': 'fail'}
        ]

        self.route = [
            {'dest': 'NodeB', 'cost': 1, 'id': 1, }
            , {'dest': 'NodeC', 'cost': 1, 'id': 2, }
            , {'dest': 'NodeD', 'cost': 1, 'id': 3, }
        ]

    def osrp_init(self): # link로부터 라우팅테이블 만들기
        for link in self.links:
            if link['status'] == 'normal':
                new = {'dest': link['dest'],'cost': 1, 'id': link['id']}
                self.route.append(new)

    def osrp_update(self): #라우팅 테이블 업데이트
        for link in self.links: # link fail시 라우팅에서 삭제
            if link['status'] == 'fail':
                link['cost'] = 0
                adj['dest'].link['node'] = 0

        for node in adj_nodes: #인접노드에서 라우팅 테이블 업데이트
            adj_routes.append(node.route) #라우팅테이블을 내 인접노드 라우팅테이블(임시)에 추가
            for adj_route in adj_routes: #인접노드 라우팅테이블의 목적지만큼
                k= route['dest'].index(adj_route['dest']) #내 라우팅테이블에도 있는지
                if k && adj_route['cost'] > route['cost']: #내 테이블의 cost값이 더 작다면
                    pass # 아무것도 하지 않음
                else:
                    route.append(adj_route) #그게 아니면 내 라우팅 테이블에 추가
