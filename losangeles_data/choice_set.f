ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
c
      PROGRAM estimate
c
ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc

      USE numerical_libraries
c   
      PARAMETER (nh=850,nparam=6,nt=100,nd=30,nf=4)
      INTEGER type(nh),bed(nh),bath(nh),iseed0,iseed1(7),
     &   iseed2,iseed3(nt),draw(nt,nd),id(nh)
      DOUBLE PRECISION rent(nh),pm(nh),tri(nh),sf(nh),
     &   crime(nh),elem(nh),sqft(nh),high(nh),
     &   a_t,b_t(5),inc_t,f(nf),sd(7),a(nt),b(5,nt),
     &   inc(nt),pran(7,nt),r1(nt),ran(7,nt),
     &   rdraw(nt,nd),r2(nd),denom(nt),util(nt,nh),
     &   prob(nt,nh),cprob(nt,nh)
c
ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
c
      OPEN(10,file='homes_LA.txt')
      REWIND(10)
      DO j=1,nh
         READ(10,*) id(j),rent(j),type(j),bed(j),bath(j),
     &      crime(j),high(j),elem(j),tri(j),sf(j),
     &      pm(j)
      enddo
c
cccccccccccccccccc
c Random Numbers c
cccccccccccccccccc
c
      iseed0 = 3570473
      call rnund(7,9999999,iseed1)
      do j = 1,7
         call rnset (iseed1(j))
         call drnun(nt,r1)
         do k = 1,nt
            pran(j,k) = r1(k)+0.5d0
         enddo 
      enddo
      iseed2 = 6601809
      call rnund(nt,9999999,iseed3)
      do j = 1,nt
         call rnset (iseed3(j))
         call drnun(nd,r2)
         do k = 1,nd
            rdraw(j,k) = r2(k)
         enddo 
      enddo
ccccccccccccccccccc
c Base Parameters c
ccccccccccccccccccc
c
      a_t = 1.d0
      b_t(1) = -0.1d0
      b_t(2) =  0.01066d0
      b_t(3) = -0.00334d0
      b_t(4) = -0.0331d0
      b_t(5) = -0.04297d0
      inc_t = 43693.d0
c
      sd(1) = 1.d0
      sd(2) = 4.d0
      sd(3) = 4.d0
      sd(4) = 4.d0
      sd(5) = 4.d0
      sd(6) = 4.d0
      sd(7) = 1.d0
c
      do k = 1,nt
         a(k) = a_t*sd(1)*pran(1,k)
         b(1,k) = b_t(1)*sd(2)*pran(2,k)
         b(2,k) = b_t(2)*sd(3)*pran(3,k)
         b(3,k) = b_t(3)*sd(4)*pran(4,k)
         b(4,k) = b_t(4)*sd(5)*pran(5,k)
         b(5,k) = b_t(5)*sd(6)*pran(6,k)
         inc(k) = inc_t*sd(7)*pran(7,k)
      enddo
c
      do k = 1,nt
         denom(k) = 0.d0
         do j = 1,nh
            if (type(j).eq.0) f(1) = 0.d0*4.d0
            if (type(j).eq.1) f(1) = 0.3762d0*4.d0 
            if (type(j).eq.2) f(1) = 0.05022d0*4.d0  
            if (bed(j).eq.1) f(2) = -0.1148d0*4.d0     
            if (bed(j).eq.2) f(2) =  0.1219d0*4.d0     
            if (bed(j).eq.3) f(2) =  0.3380d0*4.d0     
            if (bed(j).eq.4) f(2) =  0.4597d0*4.d0    
            if (bed(j).eq.5) f(2) =  0.5999d0*4.d0   
            if (bed(j).eq.6) f(2) =  0.9265d0*4.d0  
            if (bed(j).eq.7) f(2) =  1.108d0*4.d0  
            if (bed(j).eq.8) f(2) =  0.2288d0*4.d0    
            if (bed(j).eq.9) f(2) =  0.1457d0*4.d0     
            if (bed(j).eq.99) f(2) = -0.333d0*4.d0     
            if (bath(j).eq.1) f(3) = 0.d0*4.d0
            if (bath(j).eq.2) f(3) = 0.1877d0*4.d0  
            if (bath(j).eq.3) f(3) = 0.3526d0*4.d0  
            if (bath(j).eq.4) f(3) = 0.8001d0*4.d0  
            if (bath(j).eq.5) f(3) = 0.9497d0*4.d0  
            if (bath(j).eq.6) f(3) = 0.6973d0*4.d0  
            if (bath(j).eq.7) f(3) = 1.311d0*4.d0  
            if (bath(j).eq.8) f(3) = 1.112d0*4.d0  
            if (bath(j).eq.9) f(3) = 1.868d0*4.d0 
            if (rent(j).ge.inc(k)) then 
               util(k,j) = -9999999.d0
            else
               util(k,j) = (dlog(inc(k)-rent(j))+
     &                     b(1,k)*crime(j)+
     &                     b(2,k)*elem(j)+b(3,k)*tri(j)+
     &                     b(4,k)*sf(j)+b(5,k)*pm(j)+
     &                     f(1)+f(2)+f(3))*a(k)
            endif
            denom(k) = denom(k)+dexp(util(k,j))
         enddo
         do j = 1,nh
            prob(k,j) = dexp(util(k,j))/denom(k)
         enddo
      enddo
c
      do k = 1,nt
         cprob(k,1) = prob(k,1)
         do j = 2,nh
            cprob(k,j) = cprob(k,j-1)+prob(k,j)
         enddo
      enddo
c
      do k = 1,nt
         do i = 1,nd
            if (rdraw(k,i).le.cprob(k,1)) draw(k,i) = 1 
            do j = 2,nh
               if ((rdraw(k,i).gt.cprob(k,j-1)).and.
     &            (rdraw(k,i).le.cprob(k,j))) then
                  draw(k,i) = id(j)
                  go to 100
               endif
            enddo
 100        continue
         enddo
      enddo
c
      open(110,file='choice_set_output.txt')
      rewind(110)
      do j = 1,nd
         write(110,115) (draw(i,j), i = 1,nt) 
      enddo
 115  format(100i12)
      open(120,file='utility_parameter_output.txt')
      rewind(120)
      do i = 1,nt
         write(120,125) i,a(i),b(1,i),b(2,i),b(3,i),
     &      b(4,i),b(5,i),inc(i)
      enddo
 125  format(i5,7f15.4)
      open(130,file='mean_utility_values.txt')
      rewind(130)
      do j = 1,nh
         write(130,135) (util(i,j), i=1,nt)
      enddo
 135  format(100f25.5)
c
      end
c
ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
         


         
  