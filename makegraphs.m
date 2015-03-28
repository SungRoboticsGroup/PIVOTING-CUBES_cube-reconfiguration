close all
% M = xlsread('results2Dpar.xlsx');
% N = xlsread('results2D.xlsx');
% 
% sum(N(:,3)==0)
% return
% 
% figure
% plot(M(:,1),(M(:,3))./M(:,2))
% hold on
% plot(M(:,1),M./(M(:,1)),'-r')
% return
% 
% figure
% hold on
% plot(M(:,[1 1]), M(:,[2 3]), '.')
% plot(N(:,1), N(:,2), '.b')
% plot(0:105,(0:105).^2,'--k')
% plot(0:105,8.*(0:105)-20,'-r')
% axis([0 110 0 12100])
% 
% xlabel('Size of Configuration, n')
% ylabel('Time Steps to Completion')
% legend({'nonparallel','parallel'})
% grid on
% return

O = xlsread('results3D.xlsx');

figure
hold on
plot(O(:,1), O(:,2), '.b')
plot(0:140,(0:140).^2,'--k')
axis([0 110 0 12100])

xlabel('Size of Configuration, n')
ylabel('Time Steps to Completion')
grid on

