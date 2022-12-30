clc
S=table2struct(readtable('out.xlsx'));

ind = year([S.timetravel])==2022;
fprintf('Descarto 2021: Había %d, quedan %d viajes\n',length(ind),sum(ind))
S = S(ind);

fprintf('Descarto las que duran menos de 7hs, quedan %d viajes\n',sum([S.dur]>8))
% S=S([S.dur]>8);


mes  =month([S.timetravel]);
figure(1);clf
hist(mes,1:12)
ylabel('Viajes por mes')
xlabel('Mes')

for inds=1:length(S)
    S(inds).ARS = nan;
    S(inds).USD = nan;
    if startsWith(S(inds).plata,'ARS')
        plata = str2double(S(inds).plata(4:end));
        if plata >0
            S(inds).ARS = plata;
        end
    end    
    if startsWith(S(inds).plata,'USD')
        plata = str2double(S(inds).plata(4:end));
        if plata >0            
            S(inds).USD = plata;
        end
    end    
end


M = struct([]);
for indmes = 1:12
    M(indmes).anio = 2022;
    M(indmes).mes = indmes;
    indeze = mes==indmes & [S.EZE];
    M(indmes).nviajeseze = sum(indeze);
    M(indmes).viajeseze = S(indeze);
    M(indmes).ARSeze = nanmean([S(indeze).ARS]);
    M(indmes).USDeze = nanmean([S(indeze).USD]);
    indaep = mes==indmes & [S.AEP]; 
    M(indmes).nviajesaep = sum(indaep);
    M(indmes).viajesaep = S(indaep);
    M(indmes).ARSaep = nanmean([S(indaep).ARS]);
    M(indmes).USDaep = nanmean([S(indaep).USD]);    
    indotro =  mes==indmes & ~[S.AEPoEZE];
    M(indmes).nviajesotro = sum(indotro);    
    M(indmes).viajesotro = S(indotro);
    M(indmes).ARSotro = nanmean([S(indotro).ARS]);
    M(indmes).USDotro = nanmean([S(indotro).USD]);
    M(indmes).total = nansum([M(indmes).nviajeseze*M(indmes).ARSeze, ...
                      M(indmes).nviajesaep*M(indmes).ARSaep, ...
                      M(indmes).nviajesotro*M(indmes).ARSotro]);
end

figure(2);clf
bar([[M.nviajesaep];[M.nviajeseze];[M.nviajesotro]]','stacked')

figure(3);clf
plot([M.total])

figure(4);clf
plot([[M.nviajesaep];[M.nviajeseze];[M.nviajesotro]]')
legend('AEP','EZE','Otro')

writetable(struct2table(rmfield(M,{'viajeseze','viajesaep','viajesotro'})),'2022 meses.xlsx')


