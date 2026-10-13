`timescale 1ns/1ps
module systolic_array #(parameter int N=4, parameter bit PIPE=0)(
 input logic clk,rst,clear,
 input logic signed [N*8-1:0] a_left,b_top,
 output wire [N*N*32-1:0] result
);
 wire signed [7:0] a [0:N-1][0:N];
 wire signed [7:0] b [0:N][0:N-1];
 for(genvar i=0;i<N;i++) begin: row
  assign a[i][0]=a_left[i*8+:8];
  assign b[0][i]=b_top[i*8+:8];
  for(genvar j=0;j<N;j++) begin: col
   mac_pe #(.PIPE(PIPE)) pe(.clk(clk),.rst(rst),.clear(clear),
    .a_in(a[i][j]),.b_in(b[i][j]),.a_out(a[i][j+1]),.b_out(b[i+1][j]),
    .acc(result[(i*N+j)*32+:32]));
  end
 end
endmodule
