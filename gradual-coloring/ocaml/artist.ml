module type T = sig
  type color = int * int * int
  val picture : color array array ref
  val canvas : color array array ref
  val paint : string -> string -> int -> unit
end

module type ImageModule = sig
  val load : string -> Images.load_option list -> Images.t
  val save : string -> Images.save_option list -> Images.t -> unit
end

module Make (ImageIO : ImageModule) (Style : Style.T) : T = struct
  type color = int * int * int

  let picture = ref (Array.make 0 (Array.make 0 (0, 0, 0)))
  let canvas = ref (Array.make 0 (Array.make 0 (0, 0, 0)))

  let paint in_name out_name iterations =

    let image = OImages.rgb24 (OImages.load in_name []) in
    let w, h = image#width, image#height in

    picture := Array.init h (fun _ -> Array.make w (0, 0, 0));
    canvas := Array.init h (fun _ -> Array.make w (0, 0, 0));

    (* Fill picture *)
    for x = 0 to w - 1 do
      for y = 0 to h - 1 do
        let in_ = image#get x y in
        let c = (in_.Color.r, in_.Color.g, in_.Color.b) in
        !picture.(y).(x) <- c
      done;
    done;

    let rec best_step n index =
      let params = Style.make_params w h index in
      let step = Style.color_params !picture params in
      if n <= 0 then
        (Style.evaluate_step !picture !canvas step, step)
      else
        let imp = Style.evaluate_step !picture !canvas step in
        let other_imp, other_step = best_step (n - 1) index in
        if imp > other_imp then
          (imp, step)
        else
          (other_imp, other_step)
    in

    for i = 0 to iterations do
      let imp, step = best_step 10 i in
      if imp > 0 then
        Style.draw_step !canvas step
      else
        ()
    done;

    (* Make image *)
    for x = 0 to w - 1 do
      for y = 0 to h - 1 do
        let (r, g, b) = !canvas.(y).(x) in
        let c = {Color.r = r; Color.g = g; Color.b = b} in
        image#set x y c
      done;
    done;

    image#save out_name None []
end
