# Claim 6 method

For deterministic experts, evaluate Definition 4 directly. For point-mass
policies its thresholded optimal-transport cost is
`1{|q(pi(x))-q(pi(x'))|>epsilon_prime}`. At each of four epsilon values and
four grid resolutions, enumerate every pair in a local grid separated by at
most `delta_0=epsilon_q`, using `epsilon_prime=3 epsilon_q`. Record pair
counts, maximum decoded jump, and all nonzero costs. Repeat with bin width
`4 epsilon_q`, which violates the declared quantizer-error assumption and
must produce violations.

For the learned quantizer, straddle the actual Theorem 6 trigger boundary at
shrinking spacings and record both deterministic TV and relaxed-OT cost. For a
Gaussian stochastic expert, compute every quantized bin probability using
normal CDF differences and sum their categorical TV exactly. Publish 8-sigma
and 10-sigma tail refinements, omitted mass, and the data-processing gap to
the raw Gaussian TV.
