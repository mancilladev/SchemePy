(begin
  (define average
     (lambda (x y) (/ (+ x y) 2)))
  (define improve
     (lambda (guess x) (average guess (/ x guess))))
  (define good-enough?
     (lambda (guess x) (< (abs (- (square guess) x)) 0.001)))
  (define sqrt-iter
     (lambda (guess x) (if (good-enough? guess x)
                         guess
                         (sqrt-iter (improve guess x)
                                    x))))
  (sqrt 9)
  (sqrt (+ 100 37))
)
