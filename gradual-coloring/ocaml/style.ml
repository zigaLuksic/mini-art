module type T = sig
  type color = int * int * int
  type params
  type step
  val make_params : int -> int -> int -> params
  val color_params : color array array -> params -> step
  val evaluate_step : color array array -> color array array -> step -> int
  val draw_step : color array array -> step -> unit
end
;;


module Rectangles : T = struct
  type color = int * int * int
  type params = int * int * int * int
  type step =  {it : color; at : params}

  let make_params width height index =
    let dx, dy = (1 + Random.int 50, 1 + Random.int 50) in
    let x1, y1 = (Random.int (width - dx), Random.int (height - dy)) in
    (x1, y1, x1 + dx, y1 + dy)

  let color_params picture (x1, y1, x2, y2) =
    let sum_r, sum_g, sum_b = ref 0, ref 0, ref 0 in
    (for x = x1 to x2 do
      for y = y1 to y2 do
        let (r, g, b) = picture.(y).(x) in
        sum_r := !sum_r + r;
        sum_g := !sum_g + g;
        sum_b := !sum_b + b;
      done;
    done;
    let area = (x2 - x1 + 1) * (y2 - y1 + 1) in
    let new_color = (!sum_r / area, !sum_g / area, !sum_b / area) in
    {it = new_color; at = (x1, y1, x2, y2)})

  let evaluate_step picture canvas {it = (r, g, b); at = (x1, y1, x2, y2)} =
    let improvement = ref 0 in
    let imp real old now = abs(real - old) - abs(real - now) in
    (for x = x1 to x2 do
      for y = y1 to y2 do
        let (real_r, real_g, real_b) = picture.(y).(x) in
        let (old_r, old_g, old_b) = canvas.(y).(x) in
        let step_imp = 
          imp real_r old_r r + imp real_g old_g g + imp real_b old_b b
        in
        improvement := !improvement + step_imp
      done;
    done;
    !improvement)

  let draw_step canvas {it = c; at = (x1, y1, x2, y2)} =
    for x = x1 to x2 do
      for y = y1 to y2 do
        canvas.(y).(x) <- c
      done;
    done;

end



module Circles : T = struct
  type color = int * int * int
  type params = int * int * int
  type step = {it : color; at : params}

  let make_params width height index =
    let rr = 1 + Random.int 50 in
    let xx, yy = Random.int (width - 2 * rr) , Random.int (height - 2 * rr) in
    (xx + rr, yy + rr, rr)

  let color_params picture (xx, yy, rr) =
    let sum_r, sum_g, sum_b, count = ref 0, ref 0, ref 0, ref 0 in
    (for x = (xx - rr) to (xx + rr) do
      for y = (yy - rr) to (yy + rr) do
        if ((x - xx)*(x - xx) + (y - yy)*(y - yy) <= rr*rr) then
          let (r, g, b) = picture.(y).(x) in
          sum_r := !sum_r + r;
          sum_g := !sum_g + g;
          sum_b := !sum_b + b;
          count := !count + 1
        else
          ()
      done;
    done;
    if !count = 0 then count := 1 else ();
    let new_color = (!sum_r / !count, !sum_g / !count, !sum_b / !count) in
    {it = new_color; at = (xx, yy, rr)})

  let evaluate_step picture canvas {it = (r, g, b); at = (xx, yy, rr)} =
    let improvement = ref 0 in
    let imp real old now = abs(real - old) - abs(real - now) in
    (for x = (xx - rr) to (xx + rr) do
      for y = (yy - rr) to (yy + rr) do
        if ((x - xx)*(x - xx) + (y - yy)*(y - yy) <= rr*rr) then
          let (real_r, real_g, real_b) = picture.(y).(x) in
          let (old_r, old_g, old_b) = canvas.(y).(x) in
          let step_imp = 
            imp real_r old_r r + imp real_g old_g g + imp real_b old_b b
          in
          improvement := !improvement + step_imp
        else
          ()
      done;
    done;
    !improvement)

  let draw_step canvas {it = c; at = (xx, yy, rr)} =
    for x = (xx - rr) to (xx + rr) do
      for y = (yy - rr) to (yy + rr) do
        if ((x - xx)*(x - xx) + (y - yy)*(y - yy) <= rr*rr) then
          canvas.(y).(x) <- c
        else
          ()
      done;
    done;

end
