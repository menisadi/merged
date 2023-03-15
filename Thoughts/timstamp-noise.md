# Time-stamps Noise
We wish to account for the fact that the margin between two instances of the same device, presented as two different cookies, can sometimes overlap due to noise.
## The Plan
1. Given two cookies we will find the minimal set of points needed to remove in order to preserve consistency. We will attach the following scores to the set.
	- The size of the set
	- The portion of deleted points from the first cookie
	- The portion of deleted points from the second cookie
	- The total\average weight for the deleted points, when the weight is the amount of contradiction a point causes.
2. We then pick "false-merges" - pairs of cookies which we know come from different sources and we measure them using those 4 measures. Our hope is that by that we can identify a threshold score for "false with h.p".
3. T.D.B - We wish to split the timeline so the first part will be the train set and the second will be the test. 
