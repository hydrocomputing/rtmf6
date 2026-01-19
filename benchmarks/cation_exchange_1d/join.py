# coding: utf-8
df_rtmf6_sel = df_rtmf6.loc[clean_df_pht3d.index] 
diff = df_rtmf6_sel - clean_df_pht3d
rtmf6 = df_rtmf6_sel.copy()
pht3d = clean_df_pht3d.copy()
rtmf6.columns = [col + ' rtmf6' for col in rtmf6.columns]
rtmf6
pht3d.columns = [col + ' pht3d' for col in pht3d.columns]
joined = rtmf6.join(pht3d)
