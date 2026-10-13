`timescale 1ns/1ps
module tb;
 parameter int N=4;
 parameter bit PIPE=0;
 logic clk=0,rst=1,clear=0;
 logic signed [N*8-1:0] a_left=0,b_top=0;
 wire [N*N*32-1:0] result;
 int A[N][N],B[N][N],C[N][N];
 int fd,rc,count=0,half_period=5,cycles=0,reset_trials=0;
 string vectors;
 systolic_array #(.N(N),.PIPE(PIPE)) dut(.*);
 task tick;
  #(half_period); clk=1; #(half_period); clk=0; cycles++;
 endtask
 task load_edges(input int t);
  a_left=0; b_top=0;
  for(int i=0;i<N;i++) if(t-i>=0 && t-i<N) begin
   a_left[i*8+:8]=8'(A[i][t-i]); b_top[i*8+:8]=8'(B[t-i][i]);
  end
 endtask
 initial begin
  rc=$value$plusargs("VECTORS=%s",vectors);
  rc=$value$plusargs("HALF=%d",half_period);
  if(half_period<=0) $fatal(1,"HALF must be positive");
  fd=$fopen(vectors,"r"); if(fd==0) $fatal(1,"vectors missing");
  tick(); tick(); rst=0;
  while(!$feof(fd)) begin
   rc=$fscanf(fd,"%d",A[0][0]); if(rc!=1) break;
   for(int i=0;i<N;i++) for(int j=0;j<N;j++) if(i!=0 || j!=0) rc=$fscanf(fd,"%d",A[i][j]);
   for(int i=0;i<N;i++) for(int j=0;j<N;j++) rc=$fscanf(fd,"%d",B[i][j]);
   for(int i=0;i<N;i++) for(int j=0;j<N;j++) begin
    rc=$fscanf(fd,"%d",C[i][j]); if(rc!=1) $fatal(1,"truncated vectors");
   end
   // Abort a partially completed operation periodically and confirm reset recovery.
   if(count%100==0) begin
    clear=1; tick(); clear=0;
    for(int t=0;t<N;t++) begin load_edges(t); tick(); end
    rst=1; tick(); rst=0; reset_trials++;
    if(result!=='0) $fatal(1,"reset failure");
   end
   clear=1; tick(); clear=0;
   for(int t=0;t<3*N-2+int'(PIPE);t++) begin load_edges(t); tick(); end
   for(int i=0;i<N;i++) for(int j=0;j<N;j++)
    if($signed(result[(i*N+j)*32+:32]) !== C[i][j])
     $fatal(1,"MISMATCH test=%0d row=%0d col=%0d got=%0d expected=%0d",count,i,j,$signed(result[(i*N+j)*32+:32]),C[i][j]);
   count++;
  end
  // One idle edge also evaluates assertions on the last useful edge.
  a_left=0; b_top=0; tick();
  $display("PASS N=%0d PIPE=%0d TESTS=%0d CYCLES=%0d RESET_TRIALS=%0d",N,PIPE,count,cycles,reset_trials);
  $finish;
 end
endmodule
