#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <numeric>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>
using namespace std;
using Weight = int64_t;
const Weight INF = numeric_limits<Weight>::max();
struct Edge { int u, v; Weight w; };
struct Graph {
    int n;
    vector<Edge> edges;
    vector<vector<Weight>> matrix;
    vector<vector<pair<int, Weight>>> lists;
    Graph(int vertices, const vector<Edge>& input): n(vertices), edges(input) {
        if (n <= 0) throw invalid_argument("V must be positive");
        matrix.assign(n, vector<Weight>(n, -1));
        lists.resize(n);
        for (auto e: edges) {
            if(e.u < 0 || e.u >= n || e.v < 0 || e.v >= n || e.u == e.v)
                throw invalid_argument("Invalid endpoint or self-loop");
            if(e.w < 0 || e.w == INF) throw invalid_argument("Weight must be in [0, INT64_MAX-1]");
            if(matrix[e.u][e.v] != -1) throw invalid_argument("Duplicate directed edge");
            matrix[e.u][e.v] = e.w; // -1 is absent; 0 is an edge.
            lists[e.u].push_back({e.v,e.w});
        }
    }
};
struct Result { vector<Weight> distance; vector<int> predecessor; };
Weight add(Weight a, Weight b) {
    // INF is reserved, so equality also exceeds the supported finite range.
    if (a >= INF-b) throw overflow_error("Distance exceeds INT64_MAX-1");
    return a+b;
}
void source_check(const Graph& g, int s) {
    if(s < 0 || s >= g.n) throw invalid_argument("Invalid source");
}
Result matrix_array_core(const Graph& g, int s) {
    Result r{vector<Weight>(g.n,INF),vector<int>(g.n,-1)};
    vector<bool> settled(g.n,false);
    r.distance[s]=0;
    for(int step=0;step<g.n;++step) {
        int u=-1;
        // The distance array is the array priority queue.
        for(int v=0;v<g.n;++v)
            if(!settled[v] && (u==-1 || r.distance[v]<r.distance[u])) u=v;
        if(u==-1 || r.distance[u]==INF) break;
        settled[u]=true;
        for(int v=0;v<g.n;++v) if(!settled[v] && g.matrix[u][v]>=0) {
            Weight candidate=add(r.distance[u],g.matrix[u][v]);
            if(candidate<r.distance[v]) { r.distance[v]=candidate; r.predecessor[v]=u; }
        }
    }
    return r;
}
// One entry per vertex. pos[v] makes decrease-key find its entry in O(1).
struct MinHeap {
    vector<int> heap,pos;
    const vector<Weight>& key;
    MinHeap(const vector<Weight>& d):pos(d.size()),key(d) {
        heap.resize(d.size()); iota(heap.begin(),heap.end(),0); iota(pos.begin(),pos.end(),0);
        for(int i=int(heap.size())/2-1;i>=0;--i) down(i);
    }
    bool less(int a,int b) { return key[heap[a]]<key[heap[b]]; }
    void exchange(int a,int b) { swap(heap[a],heap[b]); pos[heap[a]]=a; pos[heap[b]]=b; }
    void down(int i) {
        while(true) {
            int j=i,l=2*i+1,r=l+1;
            if(l<int(heap.size()) && less(l,j)) j=l;
            if(r<int(heap.size()) && less(r,j)) j=r;
            if(j==i) break;
            exchange(i,j); i=j;
        }
    }
    void decrease(int v) {
        int i=pos[v];
        while(i>0 && less(i,(i-1)/2)) { int p=(i-1)/2; exchange(i,p); i=p; }
    }
    int pop() {
        int v=heap[0]; exchange(0,int(heap.size())-1); heap.pop_back(); pos[v]=-1;
        if(!heap.empty()) down(0);
        return v;
    }
};
Result list_heap_core(const Graph& g,int s) {
    Result r{vector<Weight>(g.n,INF),vector<int>(g.n,-1)};
    r.distance[s]=0;
    MinHeap q(r.distance);
    while(!q.heap.empty()) {
        int u=q.pop();
        if(r.distance[u]==INF) break;
        for(auto [v,w]:g.lists[u]) if(q.pos[v]!=-1) {
            Weight candidate=add(r.distance[u],w);
            if(candidate<r.distance[v]) {
                r.distance[v]=candidate; r.predecessor[v]=u; q.decrease(v);
            }
        }
    }
    return r;
}
// Public entry points validate; benchmark times only the validated cores.
Result matrix_array(const Graph& g,int s) { source_check(g,s); return matrix_array_core(g,s); }
Result list_heap(const Graph& g,int s) { source_check(g,s); return list_heap_core(g,s); }
vector<int> path(const Result& r,int s,int t) {
    int n=int(r.distance.size());
    if(s<0 || s>=n || t<0 || t>=n) throw invalid_argument("Invalid path endpoint");
    if(r.distance[t]==INF) return {};
    vector<int> p;
    for(int v=t;v!=-1;v=r.predecessor[v]) {
        if(int(p.size())>=n) throw logic_error("Predecessor cycle");
        p.push_back(v);
        if(v==s) { reverse(p.begin(),p.end()); return p; }
    }
    throw logic_error("Path does not reach source");
}
// Independent reference: repeated edge relaxation, no priority queue.
vector<Weight> bellman_ford(const Graph& g,int s) {
    vector<Weight> d(g.n,INF); d[s]=0;
    for(int pass=1;pass<g.n;++pass) {
        bool changed=false;
        for(auto e:g.edges) if(d[e.u]!=INF) {
            Weight x=add(d[e.u],e.w);
            if(x<d[e.v]) { d[e.v]=x; changed=true; }
        }
        if(!changed) break;
    }
    return d;
}
void require(bool ok,const string& message) { if(!ok) throw logic_error(message); }
void verify(const Graph& g,int s,const Result& r,const vector<Weight>& expected) {
    require(r.distance==expected,"Distance mismatch");
    for(int t=0;t<g.n;++t) {
        auto p=path(r,s,t);
        if(expected[t]==INF) { require(p.empty(),"Unreachable path"); continue; }
        require(!p.empty() && p.front()==s && p.back()==t,"Path endpoints");
        Weight sum=0;
        for(size_t i=1;i<p.size();++i) {
            Weight w=g.matrix[p[i-1]][p[i]]; require(w>=0,"Missing path edge"); sum=add(sum,w);
        }
        require(sum==expected[t],"Path weight mismatch");
    }
}
// Stable generator for cross-compiler random test reproducibility.
uint64_t state=12345;
uint64_t random_word() { state^=state<<13; state^=state>>7; state^=state<<17; return state; }
template<class F> void rejects(F f) {
    bool caught=false; try { f(); } catch(const invalid_argument&) { caught=true; }
    require(caught,"Invalid input accepted");
}
void test() {
    Graph demo(6,{{0,1,4},{0,2,0},{2,1,1},{1,3,2},{2,3,5},{3,4,3}});
    vector<Weight> expected{0,1,0,3,6,INF};
    verify(demo,0,matrix_array(demo,0),expected); verify(demo,0,list_heap(demo,0),expected);
    Graph empty(4,{}); verify(empty,2,matrix_array(empty,2),{INF,INF,0,INF});
    verify(empty,2,list_heap(empty,2),{INF,INF,0,INF});
    for(int k=0;k<300;++k) {
        int n=1+random_word()%18; vector<Edge> edges;
        for(int u=0;u<n;++u) for(int v=0;v<n;++v)
            if(u!=v && random_word()%100<static_cast<unsigned>(k%101)) edges.push_back({u,v,Weight(random_word()%21)});
        Graph g(n,edges);
        for(int s=0;s<n;++s) {
            auto d=bellman_ford(g,s); verify(g,s,matrix_array(g,s),d); verify(g,s,list_heap(g,s),d);
        }
    }
    rejects([]{Graph g(0,{});}); rejects([]{Graph g(2,{{0,2,1}});});
    rejects([]{Graph g(2,{{0,1,-1}});}); rejects([]{Graph g(2,{{0,1,INF}});});
    rejects([]{Graph g(2,{{0,0,0}});}); rejects([]{Graph g(2,{{0,1,1},{0,1,2}});});
    rejects([&]{matrix_array(demo,-1);}); rejects([&]{list_heap(demo,6);});
    rejects([&]{path(matrix_array(demo,0),0,6);});
    Graph boundary(2,{{0,1,INF-1}});
    verify(boundary,0,matrix_array(boundary,0),{0,INF-1});
    verify(boundary,0,list_heap(boundary,0),{0,INF-1});
    Graph overflow(3,{{0,1,INF-1},{1,2,1}});
    for(bool heap:{false,true}) {
        bool caught=false;
        try { if(heap) list_heap(overflow,0); else matrix_array(overflow,0); }
        catch(const overflow_error&) { caught=true; }
        require(caught,"Overflow not rejected");
    }
    cout<<"PASS: known cases, invalid inputs, overflow, 300 random graphs/all sources, distances and paths\n";
}
int main(int argc,char** argv) {
    try {
        if(argc==2 && string(argv[1])=="test") { test(); return 0; }
        if(argc==2 && string(argv[1])=="demo") {
            Graph g(6,{{0,1,4},{0,2,0},{2,1,1},{1,3,2},{2,3,5},{3,4,3}});
            for(bool heap:{false,true}) {
                auto r=heap?list_heap(g,0):matrix_array(g,0);
                cout<<(heap?"list_heap":"matrix_array")<<"\n";
                for(int t=0;t<g.n;++t) {
                    cout<<t<<": ";
                    if(r.distance[t]==INF) cout<<"unreachable";
                    else { cout<<r.distance[t]<<" path:"; for(int v:path(r,0,t)) cout<<' '<<v; }
                    cout<<'\n';
                }
            }
            return 0;
        }
        // File format: V E source, followed by E lines u v weight.
        if(argc!=5 || string(argv[1])!="run") throw invalid_argument("Usage: dijkstra test|demo|run graph.txt trials output.csv");
        ifstream in(argv[2]); int n,m,s;
        if(!(in>>n>>m>>s) || m<0) throw invalid_argument("Invalid graph header");
        vector<Edge> edges;
        for(int i=0;i<m;++i) { Edge e; if(!(in>>e.u>>e.v>>e.w)) throw invalid_argument("Invalid edge input"); edges.push_back(e); }
        string extra; if(in>>extra) throw invalid_argument("Trailing graph input");
        Graph g(n,edges); source_check(g,s);
        size_t consumed=0; int trials=stoi(argv[3],&consumed);
        if(consumed!=string(argv[3]).size() || trials<1) throw invalid_argument("Trials must be positive integers");
        auto baseline=matrix_array(g,s); auto other=list_heap(g,s);
        verify(g,s,baseline,baseline.distance); verify(g,s,other,baseline.distance);
        // Two untimed warm-up pairs; construction and validation precede timing.
        for(int i=0;i<2;++i) { matrix_array(g,s); list_heap(g,s); }
        ofstream out(argv[4]); if(!out) throw runtime_error("Cannot open output");
        out<<"algorithm,trial,order,elapsed_ms\n"; out.precision(17);
        for(int trial=0;trial<trials;++trial) for(int order=0;order<2;++order) {
            bool heap=(trial+order)%2;
            auto begin=chrono::steady_clock::now();
            auto result=heap?list_heap_core(g,s):matrix_array_core(g,s);
            auto end=chrono::steady_clock::now();
            verify(g,s,result,baseline.distance); // outside timed interval
            out<<(heap?"list_heap":"matrix_array")<<','<<trial<<','<<order<<','
               <<chrono::duration<double,milli>(end-begin).count()<<'\n';
        }
        if(!out) throw runtime_error("Output write failed");
    } catch(const exception& e) { cerr<<e.what()<<'\n'; return 1; }
}
