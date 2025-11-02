package com.example.repository;

import com.example.entity.Portfolio;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PortfolioRepository extends JpaRepository<Portfolio, Long> {
    List<Portfolio> findByModelId(Long modelId);
    
    Portfolio findByModelIdAndCoin(Long modelId, String coin);
    
    @Query("SELECT SUM(p.quantity * p.avgPrice) FROM Portfolio p WHERE p.modelId = :modelId")
    Double getTotalInvestment(@Param("modelId") Long modelId);
    
    @Modifying
    @Query("DELETE FROM Portfolio p WHERE p.modelId = :modelId")
    void deleteByModelId(@Param("modelId") Long modelId);
}