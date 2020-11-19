module Test = Artist.Make(Jpeg)(Style.Rectangles)

let () = Test.paint "corgo.jpeg" "test.jpeg" 10000
