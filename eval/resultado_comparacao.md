# Comparacao RAG vs Long Context

- Perguntas avaliadas: **25**
- Latencia media — RAG: **6.68s** | Long Context: **3.44s**
- Tokens medios — RAG: **937.24** | Long Context: **1013.2**

| # | Pergunta | Esperado | Latencia RAG | Latencia LC | Tokens RAG | Tokens LC |
|---|----------|----------|-------------|------------|-----------|----------|
| 1 | Qual a frequencia minima obrigatoria em cada disciplina? | 75% da carga horaria. | 6.8s | 3.32s | 984 | 1188 |
| 2 | Qual a nota minima para ser aprovado em uma disciplina? | Nota final igual ou superior a 6,0. | 6.15s | 3.34s | 952 | 1196 |
| 3 | Quem tem direito a fazer prova final (exame)? | Quem tiver nota final entre 4,0 e 5,9. | 5.86s | 3.66s | 891 | 1211 |
| 4 | Por quanto tempo posso trancar a matricula? | No maximo 2 semestres consecutivos. | 10.8s | 3.69s | 861 | 1210 |
| 5 | Quando o trancamento de matricula e permitido? | Somente apos a conclusao do primeiro semestre do curso. | 6.82s | 3.1s | 945 | 1171 |
| 6 | Em quantas disciplinas posso ser reprovado e ainda cursar em dependencia? | Em ate 3 disciplinas. | 6.78s | 3.89s | 945 | 1235 |
| 7 | Quais sao as penalidades disciplinares possiveis? | Advertencia verbal, advertencia escrita, suspensao e desligamento. | 6.49s | 3.62s | 1009 | 1217 |
| 8 | Quantos semestres dura o curso de ADS? | 5 semestres. | 6.23s | 3.29s | 983 | 1040 |
| 9 | Qual a carga horaria total do curso de ADS? | 2.000 horas. | 6.18s | 3.14s | 929 | 1036 |
| 10 | Como e calculada a nota final de uma disciplina? | Media aritmetica de N1 e N2. | 5.98s | 3.27s | 935 | 1042 |
| 11 | Qual o prazo para solicitar revisao de prova? | Ate 3 dias uteis apos a divulgacao da nota. | 5.93s | 3.24s | 926 | 1039 |
| 12 | Quantas horas de atividades complementares preciso cumprir? | 100 horas. | 6.32s | 3.01s | 980 | 1013 |
| 13 | Quantos livros posso pegar na biblioteca e por quantos dias? | Ate 3 livros por 14 dias. | 6.04s | 3.27s | 939 | 1034 |
| 14 | Qual a carga horaria minima do estagio obrigatorio? | 160 horas. | 6.21s | 3.29s | 956 | 912 |
| 15 | A partir de que periodo posso iniciar o estagio obrigatorio? | A partir do 4o periodo. | 5.96s | 3.33s | 900 | 922 |
| 16 | Qual a jornada maxima permitida no estagio? | 6 horas diarias e 30 horas semanais. | 6.15s | 3.45s | 880 | 915 |
| 17 | Quando posso pedir dispensa parcial do estagio obrigatorio? | Comprovando atividade profissional na area de TI por 6 meses ou mais. | 6.71s | 3.68s | 958 | 950 |
| 18 | Quantos integrantes deve ter o grupo do projeto final? | De 3 a 5 integrantes. | 6.45s | 3.55s | 886 | 887 |
| 19 | Qual o tamanho minimo do relatorio tecnico? | No minimo 15 paginas. | 10.13s | 3.08s | 903 | 867 |
| 20 | E permitido usar IA generativa no projeto final? | Sim, e permitido e incentivado, desde que o codigo seja revisado e compreendido. | 6.46s | 3.93s | 894 | 939 |
| 21 | O que acontece em caso de plagio de codigo? | Nota zero para todos os integrantes do grupo. | 6.31s | 3.49s | 859 | 905 |
| 22 | Qual o desconto de pontualidade na mensalidade? | 5% para pagamento ate o dia 5. | 6.51s | 3.49s | 987 | 839 |
| 23 | Qual a multa por atraso no pagamento da mensalidade? | Multa de 2% mais juros de 1% ao mes. | 6.62s | 3.57s | 992 | 847 |
| 24 | Qual media e desconto da bolsa de merito academico? | Media igual ou superior a 9,0, com 30% de desconto. | 6.64s | 3.94s | 1012 | 880 |
| 25 | Tenho direito a reembolso se cancelar a matricula? | 80% do valor pago se cancelar ate 7 dias apos o inicio das aulas. | 6.53s | 3.37s | 925 | 835 |

## Respostas (para inspecao manual de qualidade)

### 1. Qual a frequencia minima obrigatoria em cada disciplina?
**Esperado:** 75% da carga horaria.  
**RAG:** A frequência mínima obrigatória é de 75% (setenta e cinco por cento) da carga horária de cada disciplina.

(Fonte: regimento_academico.txt, Art. 5º)  
**Long Context:** A frequência mínima obrigatória é de 75% (setenta e cinco por cento) da carga horária de cada disciplina. (Art. 5º)

### 2. Qual a nota minima para ser aprovado em uma disciplina?
**Esperado:** Nota final igual ou superior a 6,0.  
**RAG:** A nota mínima para ser aprovado em uma disciplina é 6,0. 

Fonte: [regimento_academico.txt, trecho 7]  
**Long Context:** A nota final de cada disciplina varia de 0 (zero) a 10 (dez), sendo aprovado o estudante que obtiver nota final igual ou superior a 6,0 (seis).

### 3. Quem tem direito a fazer prova final (exame)?
**Esperado:** Quem tiver nota final entre 4,0 e 5,9.  
**RAG:** O estudante com nota final entre 4,0 e 5,9 terá direito a uma prova final (exame).  
**Long Context:** O estudante com nota final entre 4,0 e 5,9 terá direito a uma prova final (exame). Após o exame, será aprovado quem obtiver média igual ou superior a 5,0 entre a nota final e a nota do exame.

### 4. Por quanto tempo posso trancar a matricula?
**Esperado:** No maximo 2 semestres consecutivos.  
**RAG:** De acordo com o Art. 10 do Regimento Acadêmico, o trancamento de matrícula suspende temporariamente os estudos sem perda do vínculo com a instituição, pelo prazo máximo de 2 (dois) semestres consecutivos.

(Fonte: regimento_academico.txt, trecho 4)  
**Long Context:** De acordo com o Artigo 10 do Regimento Acadêmico, o trancamento de matrícula suspende temporariamente os estudos sem perda do vínculo com a instituição, pelo prazo máximo de 2 (dois) semestres consecutivos.

### 5. Quando o trancamento de matricula e permitido?
**Esperado:** Somente apos a conclusao do primeiro semestre do curso.  
**RAG:** De acordo com o Regimento Acadêmico, o trancamento de matrícula é permitido após a conclusão do primeiro semestre do curso e deve ser solicitado até o último dia útil antes do início do período de provas. O prazo máximo de trancamento é de 2 (dois) semestres consecutivos.

(Fonte: regimento_academico.txt, trecho 4)  
**Long Context:** O trancamento de matrícula é permitido após a conclusão do primeiro semestre do curso.

### 6. Em quantas disciplinas posso ser reprovado e ainda cursar em dependencia?
**Esperado:** Em ate 3 disciplinas.  
**RAG:** Segundo o Regimento Acadêmico, você pode ser reprovado em até 3 (três) disciplinas e ainda cursá-las em regime de dependência no semestre seguinte.

Fonte: regimento_academico.txt, trecho 13. Art. 13  
**Long Context:** De acordo com o Art. 13 do Regimento Acadêmico, você pode ser reprovado em até 3 (três) disciplinas e ainda cursá-las em regime de dependência no semestre seguinte, sem prejuízo das disciplinas regulares do período.

Fonte: REGIMENTO ACADÊMICO - Versão 2026.1

### 7. Quais sao as penalidades disciplinares possiveis?
**Esperado:** Advertencia verbal, advertencia escrita, suspensao e desligamento.  
**RAG:** De acordo com o Regimento Acadêmico, as penalidades disciplinares aplicáveis são:

- Advertência verbal
- Advertência escrita
- Suspensão
- Desligamento (em casos graves), observado o direito à ampla defesa.

Fonte: regimento_academico.txt, trecho 15.  
**Long Context:** As penalidades disciplinares mencionadas no documento são:

1. Advertência verbal;
2. Advertência escrita;
3. Suspensão;
4. Desligamento.

Fonte: Regimento Acadêmico do Instituto de Tecnologia Horizonte (ITH) - Versão 2026.1.

### 8. Quantos semestres dura o curso de ADS?
**Esperado:** 5 semestres.  
**RAG:** O curso de Análise e Desenvolvimento de Sistemas (ADS) tem uma duração de 5 (cinco) semestres. 

(Fonte: manual_do_aluno_ads.txt, trecho 1.1)  
**Long Context:** O curso de Análise e Desenvolvimento de Sistemas (ADS) tem uma duração de 5 (cinco) semestres.

### 9. Qual a carga horaria total do curso de ADS?
**Esperado:** 2.000 horas.  
**RAG:** A carga horária total do curso de Análise e Desenvolvimento de Sistemas (ADS) é de 2.000 horas. 

(Fonte: manual_do_aluno_ads.txt, trecho 1)  
**Long Context:** A carga horária total do curso de Análise e Desenvolvimento de Sistemas (ADS) é de 2.000 horas.

### 10. Como e calculada a nota final de uma disciplina?
**Esperado:** Media aritmetica de N1 e N2.  
**RAG:** A nota final da disciplina é a média aritmética das notas parciais N1 e N2.  
**Long Context:** A nota final da disciplina é a média aritmética das notas parciais N1 e N2, que variam de 0 a 10.

### 11. Qual o prazo para solicitar revisao de prova?
**Esperado:** Ate 3 dias uteis apos a divulgacao da nota.  
**RAG:** O prazo para solicitar revisão de prova é de até 3 dias úteis após a divulgação da nota.  
**Long Context:** O prazo para solicitar revisão de prova é de até 3 (três) dias úteis após a divulgação da nota.

### 12. Quantas horas de atividades complementares preciso cumprir?
**Esperado:** 100 horas.  
**RAG:** De acordo com o trecho 4.2 do manual do aluno ADS, você deve cumprir 100 (cem) horas de Atividades Complementares ao longo do curso.

(Fonte: manual_do_aluno_ads.txt, trecho 4.2)  
**Long Context:** 100 horas.

### 13. Quantos livros posso pegar na biblioteca e por quantos dias?
**Esperado:** Ate 3 livros por 14 dias.  
**RAG:** De acordo com o manual do aluno, você pode emprestar até 3 livros pela biblioteca por 14 dias.  
**Long Context:** Você pode emprestar até 3 livros da biblioteca por um período de 14 dias.

### 14. Qual a carga horaria minima do estagio obrigatorio?
**Esperado:** 160 horas.  
**RAG:** A carga horária mínima do Estágio Obrigatório é de 160 horas. (Fonte: política_estagio.txt, trecho 2.1)  
**Long Context:** A carga horária mínima do Estágio Supervisionado Obrigatório é de 160 (cento e sessenta) horas.

### 15. A partir de que periodo posso iniciar o estagio obrigatorio?
**Esperado:** A partir do 4o periodo.  
**RAG:** A partir do 4º período do curso. (Fonte: política_estagio.txt, trecho 2.1)  
**Long Context:** Somente pode iniciar o estágio obrigatório o aluno regularmente matriculado a partir do 4º período do curso. (SEÇÃO 2, item 2.1)

### 16. Qual a jornada maxima permitida no estagio?
**Esperado:** 6 horas diarias e 30 horas semanais.  
**RAG:** A jornada máxima permitida durante o estágio é de 6 (seis) horas diárias e 30 (trinta) horas semanais.  
**Long Context:** A jornada máxima permitida no estágio é 6 (seis) horas diárias e 30 (trinta) horas semanais.

### 17. Quando posso pedir dispensa parcial do estagio obrigatorio?
**Esperado:** Comprovando atividade profissional na area de TI por 6 meses ou mais.  
**RAG:** De acordo com a política de estágio, você pode requerer dispensa parcial do estágio obrigatório se comprovar exercício de atividade profissional na área de TI por meio de carteira de trabalho ou contrato, por período igual ou superior a 6 meses. Isso será analisado pelo Colegiado.

(Fonte: política_estagio.txt, trecho 6.1)  
**Long Context:** De acordo com a Seção 6, item 6.1, você pode requerer dispensa parcial das horas de estágio obrigatório se comprovar exercício de atividade profissional na área de TI por meio de carteira de trabalho ou contrato, por período igual ou superior a 6 meses.

### 18. Quantos integrantes deve ter o grupo do projeto final?
**Esperado:** De 3 a 5 integrantes.  
**RAG:** De acordo com o Art. 3º da normas_tcc.txt, o grupo do Projeto Integrador Final deve ter entre 3 (três) e 5 (cinco) integrantes.

(Fonte: normas_tcc.txt, trecho 3)  
**Long Context:** De acordo com o Artigo 3º do documento, o projeto deve ser desenvolvido em grupos de 3 (três) a 5 (cinco) integrantes.

### 19. Qual o tamanho minimo do relatorio tecnico?
**Esperado:** No minimo 15 paginas.  
**RAG:** De acordo com o trecho 2 do documento "normas_tcc.txt", o relatório técnico deve ter no mínimo 15 páginas. 

(Fonte: normas_tcc.txt, trecho 2)  
**Long Context:** O tamanho mínimo do relatório técnico é de 15 (quinze) páginas.

### 20. E permitido usar IA generativa no projeto final?
**Esperado:** Sim, e permitido e incentivado, desde que o codigo seja revisado e compreendido.  
**RAG:** Sim, é permitido e incentivado o uso de ferramentas de IA generativa no desenvolvimento do Projeto Integrador Final, desde que todo código gerado seja compreendido, revisado e adaptado pelo grupo. (Fonte: normas_tcc.txt, trecho 11)  
**Long Context:** Sim, é permitido e incentivado o uso de ferramentas de IA generativa no desenvolvimento do Projeto Integrador Final. No entanto, todo código gerado deve ser compreendido, revisado e adaptado pelo grupo. Além disso, o grupo deve declarar no relatório quais ferramentas de IA foram usadas e estar capaz de explicar qualquer trecho do código durante a apresentação.

### 21. O que acontece em caso de plagio de codigo?
**Esperado:** Nota zero para todos os integrantes do grupo.  
**RAG:** O plágio de código de outros grupos ou a cópia integral de projetos da internet resultará em nota zero para todos os integrantes do grupo. (Fonte: normas_tcc.txt, trecho 10)  
**Long Context:** O plágio de código de outros grupos ou a cópia integral de projetos da internet resultará em nota zero para todos os integrantes do grupo. (Fonte: NORMAS DO TRABALHO DE CONCLUSÃO DE CURSO (TCC))

### 22. Qual o desconto de pontualidade na mensalidade?
**Esperado:** 5% para pagamento ate o dia 5.  
**RAG:** O desconto de pontualidade é de 5% (cinco por cento) quando o pagamento da mensalidade é feito até o dia 5 (cinco) do mês. 

(Fonte: regras_financeiras_bolsas.txt, trecho 2.1)  
**Long Context:** O desconto de pontualidade é de 5% (cinco por cento) quando o pagamento da mensalidade é feito até o dia 5 (cinco) do mês.

### 23. Qual a multa por atraso no pagamento da mensalidade?
**Esperado:** Multa de 2% mais juros de 1% ao mes.  
**RAG:** A multa por atraso superior a 90 (noventa) dias é de 2% (dois por cento) mais juros de 1% (um por cento) ao mês sobre o valor da parcela. Fonte: [regras_financeiras_bolsas.txt, trecho 1].  
**Long Context:** A multa por atraso no pagamento da mensalidade é de 2% (dois por cento) mais juros de 1% (um por cento) ao mês sobre o valor da parcela.

### 24. Qual media e desconto da bolsa de merito academico?
**Esperado:** Media igual ou superior a 9,0, com 30% de desconto.  
**RAG:** A bolsa de Mérito Acadêmico é concedida ao aluno com média geral igual ou superior a 9,0 no semestre anterior. O valor do desconto na mensalidade é de 30% (trinta por cento). 

(Fonte: regras_financeiras_bolsas.txt, trecho 3)  
**Long Context:** A bolsa de Mérito Acadêmico é concedida ao aluno com média geral igual ou superior a 9,0 no semestre anterior. O valor do desconto na mensalidade é de 30%.

(Fonte: Documento "REGRAS FINANCEIRAS E DE BOLSAS" - Instituto de Tecnologia Horizonte (ITH) — 2026.1

### 25. Tenho direito a reembolso se cancelar a matricula?
**Esperado:** 80% do valor pago se cancelar ate 7 dias apos o inicio das aulas.  
**RAG:** Sim, você tem direito a reembolso se cancelar a matrícula até 7 dias após o início das aulas, com um desconto de 80% do valor pago no semestre. (Fonte: regras_financeiras_bolsas.txt, trecho 5.1)  
**Long Context:** Sim, você tem direito a reembolso se cancelar a matrícula até 7 (sete) dias após o início das aulas.
