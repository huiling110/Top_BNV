foreach file(crab_projects/**)

    echo 
    echo "========================================"
    echo
    echo $file
    echo
    echo "========================================"

    echo 
    echo "---------- RESUBMIT ---------"
    crab resubmit -c $file
    echo 
    echo

end
