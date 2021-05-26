% parameters to change
%  filename = string name of record file to read in
%  savefile = true/false whether to save the result as an animation
%  speedup = number of frames generated per frame saved
%
% line 22: savetype = extension of animation file to save
% line 27: TRANSFORM_TYPE = type of cubes being animated
% line 377: call to view changes the axes limits in 3D drawing

function makevideo(filename, savefile, speedup)

if ~exist('filename', 'var')
    filename = 'c4_steps.record';
end

if ~exist('savefile', 'var')
    dosave = true;
else
    dosave = savefile;
end

savetype = '.avi'; %could be .png to save series of images in a folder instead

IS_PIVOT = 0;
IS_SLIDE = 1;
IS_STRETCH = 2;
TRANSFORM_TYPE = IS_PIVOT;

add_shadow = false;

if ~exist('speedup', 'var')
    speedup = 1;
end

resolution = 2;

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

fid = fopen(filename);
taillength = 2;
niter = 0;

%figure('units','normalized','position',[.5 0 .5 1])

%try
    if dosave
        [~,fpart] = fileparts(filename);
        savename = [fpart '3D_' num2str(speedup) 'x'];
        % disp(strjoin([savename '.avi'],''));
        switch (savetype)
            case '.avi'
                % Prepare the new file.
                vidObj = VideoWriter([savename '.avi']); %[savename '.avi']);
                vidObj.FrameRate = 30;
                open(vidObj);
            case '.png'
                npic = 0;;
                if ~exist(savename, 'dir')
                    mkdir(savename);
                end
        end
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
    slice = zeros(0,3);
    
    if dim == 2
        slice = theconfig;
        theconfig = zeros(0,2);
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
                % disp(slice);
                [tf, loc] = ismember(slice, theconfig, 'rows');
                if any(tf)
                    theconfig(loc(tf),:) = [];
                end
            end
            dodraw = true;
            idx = [strfind(tline, '[Cube') length(tline)+1];
            for icube = 1:length(idx)-1
                
                thismove = tline(idx(icube):idx(icube+1)-1);
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
                    
                    if TRANSFORM_TYPE == IS_STRETCH
                        [tf, loc] = ismember(rotate(end,7:6+dim), theconfig, 'rows');
                        if tf
                            theconfig(loc,:) = [];
                        end
                        [tf, loc] = ismember(rotate(end,10:9+dim), theconfig, 'rows');
                        if tf
                            theconfig(loc,:) = [];
                        end
                    end
                else
                    theconfig(end+1,:) = sscanf(thismove(ncubes(1):end), ...
                        ['(%d' repmat(', %d', 1, dim-1)])';
                    ntail = ntail + 1;
                    dodraw = dim~=3;
                    nextline = length(tstore);
                    if length(idx) > 1 && ntail <= taillength
                        nextline = nextline + 1;
                        tstore{end+1} = tline(idx(2):end);
                        break;
                    end
                end
                
                if ntail < taillength && length(idx)>2
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
%catch e
%    disp([e.stack(1).name ': ' num2str(e.stack(1).line)])
%    disp(e.message)
%end
fclose(fid);

if dosave
    switch savetype
        case '.avi'
            % Close the file.
            close(vidObj);
        case '.png'
    end
end


    function plotpos(A, slice, rotate, dim)
        
        clf
        hold on
        
        
        if size(A,2) == 2
            A(:,3) = 0;
        end
        if size(slice,2)==2
            slice(:,3) = 0;
        end
        
        maxcoord = max([maxcoord; A; slice; rotate(:,1:3); rotate(:,4:6)]);
        
        col = [.7 .7 .7];
        alpha = 0.5;
        for iA = 1:size(A,1)
            xyz = A(iA,:);
            
            patch(CUBE_X+xyz(1), CUBE_Y+xyz(2), CUBE_Z+xyz(3),'k',...
                'facecolor',col, 'facealpha', alpha,'linewidth',2,'edgealpha',alpha);
        end
        
       col = [0 1 0];
       alpha = 1;
        for islice = 1:size(slice,1)
            xyz = slice(islice,:);
            patch(CUBE_X+xyz(1), CUBE_Y+xyz(2), CUBE_Z+xyz(3),'k',...
                  'facecolor',col, 'facealpha', alpha,'linewidth',2,'edgealpha',alpha);
        end
        
%        col = [1 1 0];
%        bcol = [1 .5 0];
%        ecol = [0 .75 1];
%        alpha = 1;
%        [extreme, b] = boundarycheck(slice);
%         for islice = 1:size(slice,1)
%             xyz = slice(islice,:);
%             if xyz == extreme
%                 patch(CUBE_X+xyz(1), CUBE_Y+xyz(2), CUBE_Z+xyz(3),'k',...
%                     'facecolor',ecol, 'facealpha', alpha,'linewidth',2,'edgealpha',alpha);
%             elseif ismember(xyz, b, 'rows')
%                 patch(CUBE_X+xyz(1), CUBE_Y+xyz(2), CUBE_Z+xyz(3),'k',...
%                     'facecolor',bcol, 'facealpha', alpha,'linewidth',2,'edgealpha',alpha);
%             else
%                 patch(CUBE_X+xyz(1), CUBE_Y+xyz(2), CUBE_Z+xyz(3),'k',...
%                     'facecolor',col, 'facealpha', alpha,'linewidth',2,'edgealpha',alpha);
%             end
%         end
        
        h = zeros(length(rotate));
        col = [1 0 1];
        alpha = 1;
        for j = linspace(0,1, resolution)
            for irotate = 1:size(rotate,1)
                if j > 0
                    if add_shadow
                        set(h(irotate), 'facealpha', 0.1, 'edgealpha',0.05)
                    else
                        delete(h(irotate))
                    end
                end
                
                xyz = rotate(irotate,:);
                
                plotTransform(xyz)
                
            end
            setaxis(dim)
            niter = niter + 1;
        end
        
        setaxis(dim)
        niter = niter + 1;
        
        function plotTransform(xyz)
            beforepos = xyz(1:3);
            afterpos = xyz(4:6);
            pivotcube = xyz(7:9);
            rotaxis = xyz(10:12);
            
            % rotaxis = intersection of beforepos, afterpos, pivotcube
            if length(find(afterpos ~= beforepos)) == 2
                % corner move
                v1 = (afterpos + beforepos) / 2;
                angle = 1;
            elseif length(find(pivotcube ~= beforepos)) == 2
                % linear move
                v1 = (pivotcube + beforepos) / 2;
                angle = 1/2;
            elseif length(find(pivotcube ~= afterpos)) == 2
                % transfer move
                v1 = (pivotcube + afterpos) / 2;
                angle = 1/2;
            end
            
            NEWC = bsxfun(@plus, [CUBE_X(:) CUBE_Y(:) CUBE_Z(:)], beforepos);
            switch (TRANSFORM_TYPE)
                case IS_PIVOT
                    NEWC = rotateAboutLinePdP(NEWC', v1, rotaxis, angle*j*pi)';
                    NEWC = reshape(NEWC, size(CUBE_X,1), size(CUBE_X,2), []);
                case IS_SLIDE
                    if angle == 1
                        dir = (afterpos-beforepos);
                        firstdir = pivotcube == afterpos;
                        if j <= .5
                            NEWC = bsxfun(@plus, NEWC, j.*firstdir.*dir);
                        else
                            NEWC = bsxfun(@plus, NEWC, firstdir.*dir + (j-.5).*(dir-firstdir));
                        end
                    else
                        NEWC = bsxfun(@plus, NEWC, j*(afterpos-beforepos));
                    end
                    NEWC = reshape(NEWC, size(CUBE_X,1), size(CUBE_X,2), []);
                case IS_STRETCH
                    if j <= .5
                        scaling = pivotcube ~= afterpos;
                        NEWC = [CUBE_X(:) CUBE_Y(:) CUBE_Z(:)];
                        scaledC = bsxfun(@times, NEWC, 1-j.*scaling);
                        NEWC = [bsxfun(@plus, scaledC, pivotcube-scaling*j/2);
                            bsxfun(@plus, scaledC, rotaxis-scaling*3*j/2);
                            bsxfun(@plus, NEWC, beforepos + 2*j*(afterpos-beforepos))];
                    else
                        scaling = pivotcube ~= afterpos;
                        NEWC = [CUBE_X(:) CUBE_Y(:) CUBE_Z(:)];
                        scaledC = bsxfun(@times, NEWC, 1-(1-j).*scaling);
                        NEWC = [bsxfun(@plus, scaledC, pivotcube-scaling*(1-j)/2);
                            bsxfun(@plus, scaledC, rotaxis-scaling*3*(1-j)/2);
                            bsxfun(@plus, NEWC, beforepos + 2*(1-j)*(afterpos-beforepos))];
                    end
                    NEWC = reshape(NEWC, size(CUBE_X,1), 3*size(CUBE_X,2), []);
            end
            
            h(irotate) = patch(NEWC(:,:,1), NEWC(:,:,2), NEWC(:,:,3),'k',...
                'facecolor',col, 'facealpha',alpha, 'linewidth', 2);
        end
        
    end

    function setaxis(dim)
        
        if dim == 2
            %view([-90,90]) % halfbug
            axis equal
            axis([-2 maxcoord(1)+2 -2 maxcoord(2)+2])
            %axis([-5 30 -5 18 -5 5]) % halfbug
            axis off
            drawnow
        else
%                 camerapos = [-150, -200, 150];
%                 if viewangle == 0
%                     set(gca,'cameraposition',camerapos)
%                     cameratar = get(gca,'CameraTarget');
%                     viewangle = get(gca,'cameraviewangle');
%                 else
%                     set(gca,'cameraposition',camerapos)
%                     set(gca,'cameratarget', cameratar)
%                     set(gca,'CameraViewAngleMode', 'auto')
%                     testangle =  get(gca,'cameraviewangle');
%                     if testangle < viewangle
%                         set(gca,'cameraviewangle', viewangle)
%                     elseif testangle > viewangle
%                         viewangle = testangle;
%                     end
%                 end
%                 set(gca,'cameraupvector',[0 0 -1])
%                 axis equal
%                 axis off
%                 drawnow
            %view(3)
            %view([0,-1,0])
            %view([-20, -10, 5]) % stalagmite_and_stalactite
            view([5, -20, 5])
            axis equal
            %axis([-2 maxcoord(1)+2 -2 maxcoord(2)+2 -2 maxcoord(3)+2])
            %axis([-2 3 -2 2 -2 4]) % halfrotation
            %axis([-2 4 -2 2 -2 4]) % stretch
            %axis([-4 4 -2 2 -2 6]) % infeasible
            %axis([-2 7 -2 7 -2 15]) % c4_steps
            %axis([-2 8 -2 8 -2 12]) % stalagmite_and_stalactite
            axis([-2 12 -2 12 -2 12]) % inbranc_L_2D
            axis off
            drawnow
        end
        
        
        % Create an animation.
        % pause
        if dosave && (mod(niter, speedup) == 0)
            switch (savetype)
                case '.avi'
                    currFrame = getframe(gcf);
                    writeVideo(vidObj,currFrame);
                case '.png'
                    print(gcf, '-dpng', [savename '\' num2str(npic) '.png']);
                    npic = npic+1;
            end
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
        ineigh = find(ismember(possneigh, slice, 'rows'), 1, 'first');
        b(end+1,:) = possneigh(ineigh,:);
        dir = dir([mod(ineigh+5,8)+1:end 1:mod(ineigh+4,8)+1],:);
        while ~all(b(end,:) == extreme)
            possneigh = bsxfun(@plus, b(end,:), dir);
            ineigh = find(ismember(possneigh, slice, 'rows'), 1, 'first');
            b(end+1,:) = possneigh(ineigh,:);
            dir = dir([mod(ineigh+5,8)+1:end 1:mod(ineigh+4,8)+1],:);
        end
        
    end

end