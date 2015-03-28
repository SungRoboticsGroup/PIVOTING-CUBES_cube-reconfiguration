function makevideo(filename, savefile)
global viewangle vidObj maxcoord dosave niter speedup

if ~exist('filename', 'var')
    filename = 'c4_steps.record';
end

if ~exist('savefile', 'var')
    dosave = false;
else
    dosave = savefile;
end

fid = fopen(filename);
niter = 0;
speedup = 6;

try
    if dosave
    % Prepare the new file.
    [~,fpart] = fileparts(filename);
    vidObj = VideoWriter([fpart '2_' num2str(speedup) 'x.avi']);
    vidObj.FrameRate = 30;
    open(vidObj);
    end
    
    % dimension
    tline = fgetl(fid);
    dim = str2double(tline);
    viewangle = 0;
    maxcoord = zeros(0,3);
    
    % config
    tline = fgetl(fid);
    tline = tline(2:end-1);
    theconfig = reshape(sscanf(tline, ['''Cube[(%d'  repmat(', %d', 1, dim-1) ')]'', ']), dim, [])';
    slice = [];
    
    if dim == 2
        slice = theconfig;
        theconfig = [];
    end
    
    %plotpos(theconfig, slice, [], dim)
    ntail = 0;
    tstore = {};
    tline = fgetl(fid);
    eof = false;
    nextline = 0;
    while (~eof)
        rotate = zeros(0, 12);
        if ~isempty(tline)
        if strcmp(tline(1:5), 'Slice')
            slice = reshape(sscanf(tline(9:end-1), ['''Cube[(%d'  repmat(', %d', 1, dim-1) ')]'', ']), dim, [])';
            [tf, loc] = ismember(slice, theconfig, 'rows');
            if any(tf)
                theconfig(loc(tf),:) = [];
            end
        end
        dodraw = true;
        idx = [strfind(tline, '[Cube') length(tline)+1];
        for i = 1:length(idx)-1
            
                thismove = tline(idx(i):idx(i+1)-1);
                ncubes = strfind(thismove, '(');
                
                if length(ncubes) > 1
                    nextcube = sscanf(thismove(ncubes(1):ncubes(2)-1), ...
                        ['(%d' repmat(', %d', 1, dim-1)])';
                    
                    % remove nextcube from theconfig
                    [tf, loc] = ismember(nextcube, slice, 'rows');
                    if tf
                        slice(loc,:) = [];
                    end
                    [tf, loc] = ismember(nextcube, theconfig, 'rows');
                    if tf
                        theconfig(loc,:) = [];
                    end
                    
                    rotate(end+1, 1:dim) = nextcube;
                    rotate(end, 4:3+dim) = sscanf(thismove(ncubes(2):ncubes(3)), ...
                        ['(%d' repmat(', %d', 1, dim-1)])';
                    rotate(end, 7:6+dim) = sscanf(thismove(ncubes(3):ncubes(4)), ...
                        ['(%d' repmat(', %d', 1, dim-1)])';
                    rotate(end, 10:12) = sscanf(thismove(ncubes(4):end), ...
                        '(%d, %d, %d)')';
                else
                    theconfig(end+1,:) = sscanf(thismove(ncubes(1):end), ...
                        ['(%d' repmat(', %d', 1, dim-1)])';
                    ntail = ntail + 1;
                    dodraw = dim~=3;
                    nextline = length(tstore);
                    if length(idx) > 1 && ntail <= 3
                        nextline = nextline + 1;
                        tstore{end+1} = tline(idx(2):end);
                        break;
                    end
                end
                
            if ntail < 3 && length(idx)>2
                tstore{end+1} = tline(idx(2):end);
                break;
            end
        end
        theconfig = unique(theconfig, 'rows');
        if dodraw
            plotpos(theconfig, slice, rotate, dim)
        end
        
        %if nextline == 1
        %    keyboard
        %end
        end
        if nextline == 0
            tline = fgetl(fid);
            if ~(ischar(tline))
                eof = true;
            end
        else
            tline = tstore{1};
            tstore = tstore(2:end);
            nextline = nextline - 1;
            %if isempty(tstore)
            %    nextline = 0;
            %end
            eof = false;
        end
        
    end
end
fclose(fid);

if dosave
% Close the file.
close(vidObj);
end
end


function plotpos(A, slice, rotate, dim)
global maxcoord niter
clf
hold on

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


if size(A,2) == 2
    A(:,3) = 0;
end
if size(slice,2)==2
    slice(:,3) = 0;
end

maxcoord = max([maxcoord; A; slice; rotate(:,1:3); rotate(:,4:6)]);

col = [.7 .7 .7];
alpha = 1;
for i = 1:size(A,1)
    xyz = A(i,:);
    
    patch(CUBE_X+xyz(1), CUBE_Y+xyz(2), CUBE_Z+xyz(3),'k',...
        'facecolor',col, 'facealpha', alpha,'linewidth',2,'edgealpha',alpha);
end

col = [1 1 0];
bcol = [1 .5 0];
ecol = [0 .75 1];
alpha = 1;
[extreme, b] = boundarycheck(slice);
for i = 1:size(slice,1)
    xyz = slice(i,:);
    
    if xyz == extreme
        patch(CUBE_X+xyz(1), CUBE_Y+xyz(2), CUBE_Z+xyz(3),'k',...
            'facecolor',ecol, 'facealpha', alpha,'linewidth',2,'edgealpha',alpha);
    elseif ismember(xyz, b, 'rows')
        patch(CUBE_X+xyz(1), CUBE_Y+xyz(2), CUBE_Z+xyz(3),'k',...
            'facecolor',bcol, 'facealpha', alpha,'linewidth',2,'edgealpha',alpha);
    else
        patch(CUBE_X+xyz(1), CUBE_Y+xyz(2), CUBE_Z+xyz(3),'k',...
            'facecolor',col, 'facealpha', alpha,'linewidth',2,'edgealpha',alpha);
    end
end

h = zeros(length(rotate));
col = [0 1 0];
alpha = 1;
for j = 0:.1:1
    for i = 1:size(rotate,1)
        if j > 0
            delete(h(i))
        end
        
        xyz = rotate(i,:);
        
        beforepos = xyz(1:3);
        afterpos = xyz(4:6);
        pivotcube = xyz(7:9);
        rotaxis = xyz(10:12);
        pivotloc = [];
        
        % rotaxis = intersection of beforepos, afterpos, pivotcube
        if length(find(afterpos ~= beforepos)) == 2
            % corner move
            v1 = (afterpos + beforepos) / 2;
            angle = pi;
        elseif length(find(pivotcube ~= beforepos)) == 2
            % linear move
            v1 = (pivotcube + beforepos) / 2;
            angle = pi/2;
        elseif length(find(pivotcube ~= afterpos)) == 2
            % transfer move
            v1 = (pivotcube + afterpos) / 2;
            angle = pi/2;
        end
        
        NEWC = bsxfun(@plus, [CUBE_X(:) CUBE_Y(:) CUBE_Z(:)], beforepos);
        NEWC = rotateAboutLinePdP(NEWC', v1, rotaxis, angle*j)';
        NEWC = reshape(NEWC, size(CUBE_X,1), size(CUBE_X,2), []);
        h(i) = patch(NEWC(:,:,1), NEWC(:,:,2), NEWC(:,:,3),'k',...
            'facecolor',col, 'facealpha',alpha, 'linewidth', 2);
        
    end
    setaxis(dim)
    niter = niter + 1;
end

setaxis(dim)
niter = niter + 1;

end

function setaxis(dim)
global viewangle cameratar vidObj maxcoord dosave niter speedup

if dim == 2
    axis equal
    axis([-2 maxcoord(1)+2 -2 maxcoord(2)+2])
    axis off
    drawnow
else
%     camerapos = [-150, -200, 150];
%     if viewangle == 0
%         set(gca,'cameraposition',camerapos)
%         cameratar = get(gca,'CameraTarget');
%         viewangle = get(gca,'cameraviewangle');
%     else
%         set(gca,'cameraposition',camerapos)
%         set(gca,'cameratarget', cameratar)
%         set(gca,'CameraViewAngleMode', 'auto')
%         testangle =  get(gca,'cameraviewangle');
%         if testangle < viewangle
%             set(gca,'cameraviewangle', viewangle)
%         elseif testangle > viewangle
%             viewangle = testangle;
%         end
%     end
%     set(gca,'cameraupvector',[0 0 -1])
%     axis equal
%     axis off
%     drawnow
view(3)
axis equal
    axis([-2 maxcoord(1)+2 -2 maxcoord(2)+2 -2 maxcoord(3)+2])
    axis off
    drawnow
end


% Create an animation.
% pause
if dosave && mod(niter, speedup) == 0
currFrame = getframe(gcf);
writeVideo(vidObj,currFrame);
end


end

function [extreme b] = boundarycheck(slice)
if isempty(slice)
    extreme = [];
    b = [];
    return
end

extreme = zeros(1,3);
extreme(3) = slice(1,3);
extreme(1) = max(slice(:,1));
extreme(2) = max(slice(slice(:,1)==extreme(1),2));

dir = [0 1 0;
    -1 1 0;
    -1 0 0;
    -1 -1 0;
    0 -1 0;
    1 -1 0;
    1 0 0;
    1 1 0];

b = extreme;
if size(slice, 1) == 1
    return
end

possneigh = bsxfun(@plus, b(end,:), dir);
i = find(ismember(possneigh, slice, 'rows'), 1, 'first');
b(end+1,:) = possneigh(i,:);
dir = dir([mod(i+5,8)+1:end 1:mod(i+4,8)+1],:);
while ~all(b(end,:) == extreme)
    possneigh = bsxfun(@plus, b(end,:), dir);
    i = find(ismember(possneigh, slice, 'rows'), 1, 'first');
    b(end+1,:) = possneigh(i,:);
    dir = dir([mod(i+5,8)+1:end 1:mod(i+4,8)+1],:);
end

end