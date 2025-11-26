program wrapper
    !
    ! Clean and compact wrapper for the MCM (SWAMI) model.
    ! Reads vectorized input from stdin, calls MCM point-by-point,
    ! and prints all output arrays back to stdout in a flat format.
    !

    use m_mcm, only: init_mcm, get_mcm, t_mcm_out
    implicit none

    ! ------------------------------------------------------------------
    ! Input variables
    ! ------------------------------------------------------------------
    integer :: length, i
    real(8) :: kps(2)
    logical :: b_winds, b_unc_std
    character(len=4096) :: data_um, data_dtm
    type(t_mcm_out) :: res

    ! Arrays allocated dynamically after reading length
    real(8), allocatable :: altitude(:), day_of_year(:), local_time(:)
    real(8), allocatable :: latitude(:), longitude(:)
    real(8), allocatable :: f107(:), f107m(:), kp1(:), kp2(:)

    ! Output arrays
    real(8), allocatable :: dens(:), temp(:), wmm(:)
    real(8), allocatable :: d_H(:), d_He(:), d_O(:)
    real(8), allocatable :: d_N2(:), d_O2(:), d_N(:)
    real(8), allocatable :: tinf(:), dens_unc(:), dens_std(:)
    real(8), allocatable :: xwind(:), ywind(:), xwind_std(:), ywind_std(:)

    ! ------------------------------------------------------------------
    ! 1. Read vector size and allocate input arrays
    ! ------------------------------------------------------------------
    read(*,*) length

    allocate( altitude(length), day_of_year(length), local_time(length), &
              latitude(length), longitude(length),                    &
              f107(length), f107m(length), kp1(length), kp2(length) )

    ! ------------------------------------------------------------------
    ! 2. Read input arrays
    ! ------------------------------------------------------------------
    read(*,*) altitude
    read(*,*) day_of_year
    read(*,*) local_time
    read(*,*) latitude
    read(*,*) longitude
    read(*,*) f107
    read(*,*) f107m
    read(*,*) kp1
    read(*,*) kp2

    read(*,*) b_winds, b_unc_std
    read(*,'(A)') data_dtm
    read(*,'(A)') data_um

    ! Initialize the SWAMI model with the provided data paths
    call init_mcm(trim(data_um), trim(data_dtm))

    ! ------------------------------------------------------------------
    ! 3. Allocate output arrays (compact grouping)
    ! ------------------------------------------------------------------
    allocate( dens(length), temp(length), wmm(length),                &
              d_H(length), d_He(length), d_O(length),                &
              d_N2(length), d_O2(length), d_N(length),               &
              tinf(length), dens_unc(length), dens_std(length),      &
              xwind(length), ywind(length), xwind_std(length), ywind_std(length) )

    ! ------------------------------------------------------------------
    ! 4. Main loop: compute each point individually
    ! ------------------------------------------------------------------
    do i = 1, length
        kps = [kp1(i), kp2(i)]

        call get_mcm( mcm_out   = res,            &
                      alti      = altitude(i),    &
                      lati      = latitude(i),    &
                      longi     = longitude(i),   &
                      loct      = local_time(i),  &
                      doy       = day_of_year(i), &
                      f107      = f107(i),        &
                      f107m     = f107m(i),       &
                      kps       = kps,            &
                      get_unc   = b_unc_std,      &
                      get_winds = b_winds )

        ! Store output
        dens(i)      = res%dens
        temp(i)      = res%temp
        wmm(i)       = res%wmm
        d_H(i)       = res%d_H
        d_He(i)      = res%d_He
        d_O(i)       = res%d_O
        d_N2(i)      = res%d_N2
        d_O2(i)      = res%d_O2
        d_N(i)       = res%d_N
        tinf(i)      = res%tinf
        dens_unc(i)  = res%dens_unc
        dens_std(i)  = res%dens_std
        xwind(i)     = res%xwind
        ywind(i)     = res%ywind
        xwind_std(i) = res%xwind_std
        ywind_std(i) = res%ywind_std
    end do

    ! ------------------------------------------------------------------
    ! 5. Write output (Python reads this in a fixed order)
    ! ------------------------------------------------------------------
    write(*,*) length

    write(*,*) altitude
    write(*,*) day_of_year
    write(*,*) local_time
    write(*,*) latitude
    write(*,*) longitude
    write(*,*) f107
    write(*,*) f107m
    write(*,*) kp1
    write(*,*) kp2

    write(*,*) dens
    write(*,*) temp
    write(*,*) wmm
    write(*,*) d_H
    write(*,*) d_He
    write(*,*) d_O
    write(*,*) d_N2
    write(*,*) d_O2
    write(*,*) d_N
    write(*,*) tinf
    write(*,*) dens_unc
    write(*,*) dens_std
    write(*,*) xwind
    write(*,*) ywind
    write(*,*) xwind_std
    write(*,*) ywind_std

    ! ------------------------------------------------------------------
    ! 6. Deallocate arrays (compact block)
    ! ------------------------------------------------------------------
    deallocate( altitude, day_of_year, local_time, latitude, longitude, &
                f107, f107m, kp1, kp2,                                 &
                dens, temp, wmm, d_H, d_He, d_O, d_N2, d_O2, d_N,      &
                tinf, dens_unc, dens_std, xwind, ywind, xwind_std, ywind_std )

end program wrapper
