% rotate about line in 3D
% function rot = rotateAboutLinePdP(p, a, axis, theta)
% p = points
% a = point in 3D
% axis = direction of line
% theta = rotation angle
function rot = rotateAboutLinePdP(p, a, axis, theta)
matrix = vrrotvec2mat([axis theta]);
rot = bsxfun(@plus, matrix*bsxfun(@minus,p,a'), a');
end