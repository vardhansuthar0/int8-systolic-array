`timescale 1ns/1ps
module mac_pe #(parameter bit PIPE=0)(
 input logic clk, rst, clear,
 input logic signed [7:0] a_in,b_in,
 output logic signed [7:0] a_out,b_out,
 output logic signed [31:0] acc
);
 logic signed [15:0] product, product_q;
 assign product = a_in * b_in;
 always_ff @(posedge clk) begin
  if(rst || clear) begin a_out<=0; b_out<=0; acc<=0; product_q<=0; end
  else begin
   a_out<=a_in; b_out<=b_in; product_q<=product;
   acc<=acc + (PIPE ? {{16{product_q[15]}},product_q} : {{16{product[15]}},product});
  end
 end
`ifndef SYNTHESIS
 // Four property definitions, instantiated in every PE; simulation assertions, not formal proofs.
 a_reset: assert property (@(posedge clk) (rst || clear) |=> acc==0 && a_out==0 && b_out==0 && product_q==0);
 a_forward: assert property (@(posedge clk) !(rst || clear) |=> a_out==$past(a_in));
 b_forward: assert property (@(posedge clk) !(rst || clear) |=> b_out==$past(b_in));
 a_accumulate: assert property (@(posedge clk) !(rst || clear) |=>
  acc == $past(acc) + (PIPE ? 32'($signed($past(product_q))) : 32'($signed($past(product)))));
`endif
endmodule
