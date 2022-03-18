void loop(double *c, double *b, double*a, long stepc, long stepb, long stepa, long n){
 while(n--){
  *c = *b + *a;
  a += stepa;
  b += stepb;
  c += stepc;
  }
}