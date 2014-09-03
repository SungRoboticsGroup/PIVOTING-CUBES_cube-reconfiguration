function plotCubes(filename)

if ~exist('filename', 'var')
    filename = 'reversible.csv';
end

A = csvread(filename);

clf
%figure; hold on;

CUBE_X = [-.5 -.5 .5 .5;
          -.5 -.5 .5 .5;
          -.5 -.5 .5 .5;
          -.5 -.5 .5 .5;
          -.5 -.5 -.5 -.5;
          .5 .5 .5 .5]';
      
CUBE_Y = [-.5 .5 .5 -.5;
          -.5 .5 .5 -.5;
          -.5 -.5 -.5 -.5;
          .5 .5 .5 .5;
          -.5 -.5 .5 .5;
          -.5 -.5 .5 .5]';

CUBE_Z = [-.5 -.5 -.5 -.5;
          .5 .5 .5 .5;
          -.5 .5 .5 -.5;
          -.5 .5 .5 -.5;
          -.5 .5 .5 -.5;
          -.5 .5 .5 -.5]';
      
for i = 1:size(A,1)
    xyz = A(i,1:3);
    col = A(i,4:6);
    alpha = A(7);
    
    if false%i==3
        M = vrrotvec2mat([0 1 0 pi/6]);
        NEWC = (M*[CUBE_X(:) CUBE_Y(:) CUBE_Z(:)]')';
        NEWC = bsxfun(@minus, NEWC, NEWC(3,:)-[.5 .5 -.5]);
        NEWC = reshape(NEWC, size(CUBE_X,1), size(CUBE_X,2), []);
        patch(NEWC(:,:,1)+A(i,1), NEWC(:,:,2)+A(i,2), NEWC(:,:,3)+A(i,3),'k',...
            'facecolor', A(i,4:6), 'facealpha', A(i,7));
    else
        patch(CUBE_X+A(i,1), CUBE_Y+A(i,2), CUBE_Z+A(i,3),'k',...
            'facecolor', A(i,4:6), 'facealpha', A(i,7),'linewidth',2,'edgealpha', A(i,7));
    end
end

axis equal

return